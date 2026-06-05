---
name: restore-function-signatures
description: Restore degraded function signatures in decompiled C/C++ code. Recovers return types, parameter types, parameter names, calling conventions, and dropped parameters (signature downgrade from UB). Triggers on "restore function signatures", "fix function signatures", "recover signature", "fix return type", "fix parameter types", "rename parameters", "fix calling convention", "fix UB downgrade", "restore dropped parameters".
version: 1.0.0
---

# Function Signature Restoration

Comprehensive function signature restoration for decompiled C/C++ pseudocode (IDA Pro / Hex-Rays, Ghidra, angr). When the decompiler produces generic signatures like `__int64 sub_401230(__int64 a1, int a2)`, restore them to meaningful forms like `int verify_password(char *pwd, int len)`.

---

## CRITICAL: Memory Semantics Above All Syntax Rules

**This section is the supreme rule. It overrides ALL other repair rules when there is a conflict.**

Decompiled code has pervasive type loss — variables that were originally pointers are often recognized as `_QWORD`, `int`, `unsigned __int64`, or other scalar types by the decompiler. Your task is to restore the **underlying memory logic**, NOT to tamper with that logic to eliminate compiler warnings. All repairs must preserve the original memory read/write paths, dereference levels, and data-flow edges — no adding `&` to "fix" a type mismatch, no changing pointer dereference depth, no altering the physical stack or heap access patterns.

---

## CRITICAL: File Integrity — NEVER Truncate the Target File

**The `Write` tool overwrites the ENTIRE file.** If you read only part of a large file then use `Write`, the unread portion is destroyed. This is the #1 cause of catastrophic data loss in automated repair.

### Mandatory Rules

1. **Read the ENTIRE file before any Write.** Use `Read` without offset/limit. If the file is too large, use `Edit` exclusively.
2. **Prefer `Edit` over `Write` for ALL changes.** Signature edits, type replacements, parameter renames — all should use `Edit`. `Write` is a last resort.
3. **After every modification, verify:** `test -s <file>.c` (non-empty check), then `wc -l <file>.c` (sanity check line count).

---

## Pipeline Overview

```
INPUT: decompiled .c file (compilable, but with degraded function signatures)
  │
  ▼
SCAN — Identify all function definitions in the file
  │  For each function, classify degradations across 5 dimensions.
  │
  ▼
CLASSIFY — Categorize each degradation found
  │
  │  D1: Generic return type     — __int64, __int32, unsigned __int64, void-when-should-not-be
  │  D2: Generic parameter types — __int64, _QWORD, unsigned __int64, int for pointer roles
  │  D3: Generic parameter names — a1, a2, a3, ... (decompiler default names)
  │  D4: Calling convention      — __fastcall, __stdcall, __cdecl, __thiscall (check correctness)
  │  D5: Dropped parameters      — ((ret (*)())func)(), forced arg-stripping casts
  │
  ├─ NO DEGRADATIONS → DONE. "No signature degradation detected."
  │
  └─ DEGRADATIONS FOUND → CROSS-VALIDATION (per dimension, per function)
       │
       ├─ CANNOT DETERMINE → SKIP that dimension for that function. Annotate.
       │
       └─ DETERMINED → RESTORE
              │  Apply type/name/convention fixes
              │
              ▼
            VERIFY — Recompile with strict gcc
              │  Fix any introduced errors (do NOT revert restoration)
              │
              ▼
            DONE — Report all restorations
```

### When to Apply Each Dimension

Not every function needs every dimension restored. Evaluate each dimension independently:

| Dimension | When to apply | When to skip |
|-----------|--------------|--------------|
| D1: Return type | Return type is generic integer (`__int64`, `__int32`) or suspicious `void` | Return type is already a proper C type (`int`, `char *`, `HRESULT`, `BOOL`) |
| D2: Parameter types | Parameter types are generic (`__int64`, `_QWORD`) or wrong-width for usage | Parameter types already match usage patterns |
| D3: Parameter names | Parameters named `a1`-`aN` or `v1`-`vN` | Parameters already have meaningful names |
| D4: Calling convention | Convention is missing, redundant (x64), or contradicts call sites | Convention is correct for the target ABI and function type |
| D5: Dropped parameters | Inline cast strips args from function call; mismatch with true signature | Call uses correct signature without argument-stripping casts |

---

## 1. Detection: Scanning Function Signatures

### 1.1 Function Definition Pattern

Scan the `.c` file for all function definitions. Match against these patterns:

```
RETURN_TYPE  FUNC_NAME  ( PARAM_LIST )
RETURN_TYPE  CONVENTION  FUNC_NAME  ( PARAM_LIST )
```

where `RETURN_TYPE` may be `__int64`, `__int32`, `int`, `void`, `unsigned __int64`, `HRESULT`, `BOOL`, `char *`, `void *`, etc., and `CONVENTION` may be `__fastcall`, `__stdcall`, `__cdecl`, `__thiscall`, `__vectorcall`, or absent.

### 1.2 Degradation Detection Rules

#### D1: Generic Return Type

| Signal | Pattern | Confidence |
|--------|---------|------------|
| `__int64` / `unsigned __int64` return type | `^__int64\s+\w+\(` | HIGH |
| `__int32` / `unsigned __int32` return type | `^unsigned? __int32\s+\w+\(` | HIGH |
| `void` return but function result is used at call sites | Caller checks/assigns return value | MEDIUM |

#### D2: Generic Parameter Types

For each parameter in the function signature, flag if:
- Type is `__int64`, `unsigned __int64`, `_QWORD` → likely a pointer on 64-bit
- Type is `__int32`, `unsigned __int32`, `_DWORD` → could be pointer on 32-bit or integer
- Type is `int` but used exclusively as a pointer in the function body

#### D3: Generic Parameter Names

Flag parameters whose names match the decompiler default naming pattern:
- `a1`, `a2`, `a3`, ... (IDA Pro default argument names)
- `v1`, `v2`, `v3`, ... (occasionally used for parameters too)
- `param_1`, `param_2`, ... (Ghidra style)

#### D4: Calling Convention Issues

Flag calling conventions when:
- `__fastcall` on x86-64 — redundant (MS x64 uses fastcall-like by default; System V uses registers)
- `__stdcall` on a variadic function — impossible (variadic functions must be `__cdecl`)
- Missing calling convention on x86 where `__stdcall` is expected (e.g., DLL exports)
- `__thiscall` on a non-member function
- Convention on x64 that contradicts actual usage (all x64 uses register passing)

#### D5: Dropped Parameters (Signature Downgrade)

| Pattern | grep/regex hint | Severity |
|---------|-----------------|----------|
| `((ret_type (*)())func)()` | `\(\(\s*\w+\s*\(\s*\*\s*\)\s*\(\s*\)\s*\)\s*\w+\s*\)\s*\(\s*\)` | HIGH |
| `((ret_type (*)(args))func)(...)` | `\(\(\s*\w+\s*\(\s*\*\s*\)\s*\([^)]*\)\s*\)\s*\w+\s*\)\s*\(` | MEDIUM |

---

## 2. Cross-Validation: Determining Correct Signatures

### 2.1 Cross-Validation Priority (All Dimensions)

For each degraded dimension, search for the true signature using this priority order:

| Priority | Source | What it reveals |
|----------|--------|-----------------|
| 1 | **Standard library / well-known API** | If function name matches a known API (`printf`, `malloc`, `CreateFileW`, `send`, `open`, etc.), use the documented signature directly. |
| 2 | **Extern declaration** in the same file | Full signature: return type, param types, param names, calling convention |
| 3 | **Call sites** — how the function is called | Argument types actually passed; how return value is used |
| 4 | **Function body** — how parameters and return value are used internally | Parameter roles, pointee types, return value semantics |
| 5 | **Domain / API ecosystem context** | LLM knowledge of common API patterns (e.g., first arg to `send` is `SOCKET`, returns `int`) |

### 2.2 Return Type Recovery (D1)

Analyze how the return value is **used at call sites** and **produced in the function body**:

| Evidence in function body | Likely return type |
|---------------------------|-------------------|
| `return 0;` / `return -1;` / `return 1;` on success/failure paths | `int`, `BOOL`, `HRESULT` |
| `return ptr;` where ptr is `void *` / `char *` | Pointer type matching the returned variable |
| `return v1;` where v1 is compared against `-1` at call sites | `int` or `ssize_t` |
| `return v1;` where v1 is checked as boolean (`if (func())`) | `BOOL` or `int` |
| `return v1;` where v1 is cast to pointer at call site | `void *` or the specific pointer type |
| `return 0;` at end after error cleanup with `goto` | `int` (error code) |
| Function never returns (infinite loop, `exit()`) | `void` or `__noreturn void` |

**Decision rule**: If call sites assign the return value to a typed variable, use that type. If call sites pass the return value directly to a known API, use that API's expected parameter type.

**Known return types for standard APIs**:
- `malloc` / `calloc` / `realloc` → `void *`
- `strlen` → `size_t`
- `open` / `socket` / `accept` → `int` (fd)
- `printf` / `fprintf` → `int`
- `strcmp` / `memcmp` → `int`
- Windows `CreateFileW` / `CreateFileA` → `HANDLE` (`void *`)

### 2.3 Parameter Type Recovery (D2)

For each generic-typed parameter, determine the true type from how it is **used in the function body**:

| Usage pattern in body | Likely parameter type |
|-----------------------|----------------------|
| Passed to `strlen()`, `strcmp()`, `strcpy()` as source | `const char *` |
| Passed to `memcpy()`, `read()`, `write()` as buffer | `void *` or `char *` |
| Passed to `free()` | `void *` |
| Compared against `NULL` / `0` with error return path | Likely a pointer |
| Dereferenced with `*param` or `param->field` | Pointer to dereferenced type |
| Passed to `malloc(n)` or used in arithmetic for allocation size | `size_t` or `int` |
| Used as array subscript | `int` or `size_t` |
| Used as loop bound | `int`, `size_t`, `unsigned int` |
| Passed as fd to `read`/`write`/`close` | `int` |
| Used in bitwise ops (`&`, `|`, `^`, `~`) | Integer type (unsigned preferred) |
| Cast to pointer type before use | The target pointer type of the cast |

**ABI constraints**:
- On 64-bit: `_QWORD` / `__int64` (8 bytes) → can be a pointer. `_DWORD` / `__int32` (4 bytes) → cannot be a 64-bit pointer.
- On 32-bit: `_DWORD` / `__int32` → can be a pointer.
- Determine target ABI from context (function uses `__fastcall` → likely Windows; 64-bit pointers → 64-bit ABI).

### 2.4 Parameter Name Recovery (D3)

Infer semantic names from how the parameter is used in the function body. This mirrors the `variable-semantic-recovery` skill's role analysis framework, applied specifically to parameters:

| Role | Body usage signals | Candidate names |
|------|-------------------|-----------------|
| **String input** | Passed to `strlen`/`strcmp`/`strcpy`/`printf("%s",...)` | `str`, `input`, `name`, `path`, `filename`, `message`, `key` |
| **Buffer destination** | dest arg to `memcpy`/`strcpy`/`read`/`recv`; allocated from `malloc` | `buf`, `dest`, `out`, `data`, `dst` |
| **Length / Size** | Passed as size/count to `malloc`/`memcpy`/`read`/`write`; loop bound | `len`, `size`, `count`, `n`, `buf_len`, `maxlen` |
| **File descriptor / Socket** | First arg to `read`/`write`/`close`/`send`/`recv` | `fd`, `sockfd`, `sock`, `handle` |
| **Opaque context / Handle** | Passed through to multiple functions, stored but rarely dereferenced directly | `ctx`, `handle`, `conn`, `session`, `state` |
| **Flag / Options** | Used in bitwise ops; compared against constants; passed to flags parameter | `flags`, `mode`, `options` |
| **Offset / Position** | Used in pointer arithmetic or as seek offset | `offset`, `pos`, `cursor`, `base` |
| **Element count** | Used as array size, loop bound nested with array access | `count`, `n`, `num`, `nelems` |
| **Format string** | First arg to `printf`/`sprintf` family | `fmt`, `format` |
| **Error code / Status** | Compared against error constants; used in return path decisions | `err`, `status`, `rc` |
| **Structure / Record pointer** | Dereferenced as `param->field` or `param->subfield->deeper` | Name after the struct type or domain role |

**Naming rules**:
1. If the function name gives domain context (e.g., `verify_password`), derive names from that domain (`pwd`, `hash`)
2. If multiple parameters share the same role, disambiguate (`src` vs `dst`, `input_buf` vs `output_buf`)
3. Prefer single-word names when clear; multi-word only when needed for disambiguation
4. If the parameter corresponds to a known API parameter, use the API convention (e.g., `flags` for the last arg of `open()`)

### 2.5 Calling Convention Cleanup (D4)

#### Rules for x86-64 (Most Common)

On x86-64, calling convention annotations are almost always unnecessary:

| Platform | Default convention | When to annotate |
|----------|-------------------|-----------------|
| Windows x64 | `__fastcall`-like (rcx, rdx, r8, r9) | Only `__vectorcall` for SIMD-heavy functions |
| Linux/macOS x64 | System V AMD64 (rdi, rsi, rdx, rcx, r8, r9) | Never — no annotations exist in standard C |

**Rule for x64**: If the function or its callers use x64 register-width types (`__int64`, `_QWORD`), **remove** `__fastcall` / `__stdcall` / `__cdecl` — they are either redundant or misleading. The ABI is implicit.

#### Rules for x86 (Legacy)

On x86, calling conventions matter:

| Signal | Correct convention |
|--------|-------------------|
| Function is a DLL export, uses `stdcall` name mangling (`_FuncName@N`) | `__stdcall` |
| Function calls use caller cleanup (stack adjustment after call) | `__cdecl` |
| Function performs callee cleanup (`ret N` in disassembly) | `__stdcall` |
| Function is a C++ member function | `__thiscall` |
| Function is variadic (`...`) | MUST be `__cdecl` |
| No evidence either way; standard C function | `__cdecl` (default) |

**Cleanup rule**: If all call sites consistently show one convention but the definition has another (or none), apply the consistent convention. If evidence is mixed, keep the declaration as-is and annotate.

### 2.6 Signature Downgrade Recovery (D5)

This is the original `recover-signature-downgrade` use case — restoring parameters dropped by the decompiler due to Use-Before-Def (CWE-457) patterns.

#### Detection

Scan for inline function pointer casts that strip or reduce function arguments:

| Pattern | Severity | Description |
|---------|----------|-------------|
| `((ret_type (*)())func)()` | HIGH | Function forced to zero arguments |
| `((ret_type (*)(fewer_args))func)(...)` | MEDIUM | Function forced to fewer/different args |

#### Cross-Validation for Dropped Parameters

Search for the true signature. Priority order same as above (Section 2.1).

**If no true signature can be found at any priority level:**
→ **STOP.** Report: `"Cannot determine true signature for '<func>'. Skipping recovery."` Do NOT guess.

#### False Positive Check

Compare parameter counts:
- Count parameters in the true signature
- Count parameters in the degraded cast
- If equal → NOT a downgrade, SKIP
- If true has MORE → IS a downgrade → PROCEED

#### Restoration for Dropped Parameters

1. Declare `UNINIT_RECOVERED_arg<N>` dummy variables for each dropped parameter (N = 1-based position in true signature)
2. Remove the inline cast, restore normal function call with all arguments
3. Do NOT initialize the dummy variables — preserving CWE-457 data flow is the goal
4. Mark with `// Restored AST: UB parameter loss recovered`

See Section 3.5 for detailed rules.

---

## 3. Restoration Rules

### 3.1 General Rules (All Dimensions)

1. **Evidence-gated**: Apply restoration only when cross-validation produces HIGH confidence. When evidence is ambiguous, preserve the original and annotate.
2. **Mark all changes**: Every modification must be marked with a `// Recovered:` comment citing the specific evidence.
3. **No logic alteration**: Only change the signature line and related declarations. Do not modify function body logic, control flow, or data flow.
4. **Fix forward**: If compilation breaks after restoration, fix with casts or `extern` declarations — do NOT revert the recovery.
5. **Dimension independence**: Each of D1-D5 is applied independently. Success/failure in one dimension does not affect others.

### 3.2 Return Type Restoration (D1)

Replace the generic return type in the function definition and all corresponding `extern`/forward declarations.

```c
// Before:
__int64 verify_password(__int64 a1, int a2) { ... }
// Call site: int result = verify_password(pwd, len);

// After:
// Recovered: return type __int64 → int — callers assign to int and compare against -1
int verify_password(__int64 a1, int a2) { ... }
```

### 3.3 Parameter Type Restoration (D2)

Replace generic parameter types in the function definition and all declarations.

```c
// Before:
__int64 verify_password(__int64 a1, int a2) {
    if (!a1) return -1;                           // null check → a1 is a pointer
    size_t len = strlen((const char *)a1);         // passed to strlen → a1 is const char *
    if (len != a2) return -2;                      // a2 compared with len → a2 is size_t
    ...
}

// After:
// Recovered: a1 type __int64 → const char * — null-checked(@L2), passed to strlen(@L3)
// Recovered: a2 type int → size_t — compared against strlen result(@L4)
int verify_password(const char *a1, size_t a2) { ... }
```

**Cast removal rule**: When a parameter type is upgraded from scalar to pointer, remove inline casts in the function body that were compensating for the wrong type:

```c
// Before (int a1 used as pointer):
void func(int a1) {
    char *s = (char *)a1;  // cast needed because a1 was declared int
    ...
}

// After (a1 is now char *):
// Recovered: a1 type int → char * — cast to char* in body
void func(char *a1) {
    char *s = a1;  // no cast needed
    ...
}
```

### 3.4 Parameter Name Restoration (D3)

Replace `a1`-`aN` names with semantic names. Preserve type and position.

```c
// Before:
__int64 sub_401230(__int64 a1, int a2, __int64 a3) {
    if (!a1 || !a3) return -1;
    if (strlen((const char *)a1) != a2) return -2;
    memcpy((void *)a3, (const void *)a1, a2);
    return 0;
}

// After:
// Recovered: a1 → pwd — used as string source for strlen(@L2) and memcpy(@L3)
// Recovered: a2 → len — compared against strlen result(@L2), used as memcpy count(@L3)
// Recovered: a3 → dest — destination buffer in memcpy(@L3), null-checked(@L1)
__int64 sub_401230(__int64 pwd, int len, __int64 dest) { ... }
```

**Conflict with variable-semantic-recovery**: Parameter name recovery overlaps with the `variable-semantic-recovery` skill for local variables. When both skills are applied, this skill handles function **parameters** (`a1`-`aN` in the signature), while `variable-semantic-recovery` handles **local variables** (`v1`-`vN` in the body). The naming conventions and evidence rules are compatible.

### 3.5 Calling Convention Restoration (D4)

**Add** missing conventions when evidence supports it. **Remove** redundant/wrong conventions when they contradict the ABI or call sites.

```c
// Before (x86 DLL export):
int __stdcall DllExportFunc(int a1, char *a2) { ... }  // __stdcall is correct

// Before (x64 code, redundant):
__int64 __fastcall sub_401000(__int64 a1) { ... }

// After:
// Recovered: removed __fastcall — redundant on x64 (implicit ABI)
__int64 sub_401000(__int64 a1) { ... }
```

**Variadic constraint**: If a function uses `...`, the calling convention MUST be `__cdecl` (on x86). On x64, remove any convention annotation — it's implicit.

```c
// Before (x86, wrong convention):
void __stdcall log_error(const char *fmt, ...) { ... }

// After:
// Recovered: __stdcall → __cdecl — variadic functions require __cdecl on x86
void __cdecl log_error(const char *fmt, ...) { ... }
```

### 3.6 Signature Downgrade Restoration (D5)

Detailed rules for restoring dropped parameters:

1. **Explicit Naming Convention:** Recovered variables MUST be named with prefix `UNINIT_RECOVERED_arg<N>`. `N` is the **1-based position** in the true function signature. If only parameter 2 was dropped, inject only `UNINIT_RECOVERED_arg2` — the numbering gap is intentional and signals to SAST tools which arguments were preserved.

2. **STRICTLY NO INITIALIZATION:** Do NOT assign any default value (`= 0`, `= NULL`). Initializing destroys the CWE-457 vulnerability being exposed.

3. **No Logic Alteration:** Only rewrite the specific line containing the degraded call. Do not change surrounding code.

4. **Mark Changes:** Mark all restored lines with: `// Restored AST: UB parameter loss recovered`.

5. **Type Matching:** The `UNINIT_RECOVERED_` variable must match the exact type from the true signature.

6. **Variadic Functions:** If the true signature ends with `...` (e.g., `int printf(const char *fmt, ...)`), inject at minimum the first required argument as `UNINIT_RECOVERED_arg1`. Add comment `// Restored AST: variadic arguments not recovered`. Do NOT inject dummy arguments for the variadic tail.

7. **Unused Variable Mitigation:** If strict compilation flags reject unused variables, add `__attribute__((unused))` — do NOT initialize.

#### D5 Examples

**Total Argument Loss:**

```c
// Before:
__int64 CWE457_bad() {
    return ((__int64 (*)())printLine)();
}
// True signature: extern __int64 printLine(const char *);

// After:
__int64 CWE457_bad() {
    // Restored AST: UB parameter loss recovered
    const char * UNINIT_RECOVERED_arg1;
    return printLine(UNINIT_RECOVERED_arg1);
}
```

**Partial Argument Loss:**

```c
// Before:
int process_data(int a) {
    return ((int (*)(int))encrypt)(a);
}
// True signature: extern int encrypt(int data, char *key);

// After:
int process_data(int a) {
    // Restored AST: UB parameter loss recovered
    char * UNINIT_RECOVERED_arg2;
    return encrypt(a, UNINIT_RECOVERED_arg2);
}
```

---

## 4. Combined Restoration: Complete Example

Showing all 5 dimensions applied together:

**Before:**
```c
__int64 __fastcall sub_401230(__int64 a1, int a2) {
    if (!a1) return -1;
    size_t v1 = strlen((const char *)a1);
    if (v1 != a2) return -2;
    if (check_hash((const char *)a1, a2) != 0) return -3;
    return 0;
}
```

**Cross-validation:**
- Call sites: `int ok = sub_401230(input, len);` — return assigned to `int`, compared against 0
- `a1` null-checked, passed to `strlen`, `check_hash` as `const char *` → `const char *`
- `a2` compared with `strlen` result (`size_t`) → `size_t`
- Function checks password validity → domain: authentication
- x64 code → `__fastcall` is redundant

**After:**
```c
// Recovered: return type __int64 → int — callers assign to int and test against 0
// Recovered: removed __fastcall — redundant on x64
// Recovered: a1 → pwd (const char *) — null-checked(@L2), passed to strlen(@L3), passed to check_hash(@L5)
// Recovered: a2 → len (size_t) — compared against strlen result(@L4), passed to check_hash
int sub_401230(const char *pwd, size_t len) {
    if (!pwd) return -1;
    size_t v1 = strlen(pwd);
    if (v1 != len) return -2;
    if (check_hash(pwd, len) != 0) return -3;
    return 0;
}
```

---

## 5. Restoration Workflow Per Function

For each function in the file, process in this order:

```
1. DETECT — Which of D1-D5 apply?
2. CROSS-VALIDATE — For each applicable dimension, find evidence.
3. DECIDE — Per dimension: apply, skip (insufficient evidence), or annotate (ambiguous).
4. APPLY — Edit the function signature line and all extern/forward declarations.
   Apply in this order: D4 (convention) → D1 (return type) → D2 (param types) → D3 (param names)
   Process D5 (dropped params) LAST — it operates on call sites, not the definition.
5. VERIFY — Recompile.
```

### Multi-Function Coordination

When multiple functions call each other, restore signatures in dependency order:
- If `foo` calls `bar`, restore `bar`'s signature first (call site evidence in `foo` is more reliable)
- When a function's signature changes, update all its call sites and declarations

---

## 6. Compilation Verification

After all restorations, recompile with strict gcc:

```bash
gcc -c -Werror=implicit-function-declaration -Werror=implicit-int \
    -Werror=incompatible-pointer-types -Werror=int-conversion \
    -Werror=return-type -fno-builtin -fmax-errors=0 -I.
```

### Common Post-Restoration Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `incompatible pointer types` after type upgrade | Parameter type changed but call sites pass different type | Add explicit cast at call site: `func((const char *)var)` |
| `unused variable` for `UNINIT_RECOVERED_*` | Strict `-Werror=unused-variable` | Add `__attribute__((unused))`. Do NOT initialize. |
| `implicit declaration of function` | Restored function has no visible declaration | Add `extern` declaration matching the restored signature. |
| `too few arguments` after D5 restoration | Not all dropped parameters accounted for | Revisit cross-validation — a parameter in the true signature has no corresponding `UNINIT_RECOVERED_` variable. |
| `conflicting types` for function | Multiple declarations with different restored signatures | Ensure all declarations and the definition use the same restored signature. |
| `error: variadic function must be __cdecl` | `...` function has wrong convention | Change to `__cdecl` (x86) or remove convention annotation (x64). |

If new errors are introduced:
1. Fix them forward (add casts, `extern` declarations, `__attribute__((unused))`).
2. Do NOT revert the signature restoration.
3. Recompile until clean (zero errors, `.o` file produced).

---

## 7. Final Report Format

```
=== Function Signature Restoration Complete ===
File: <filename>
Functions analyzed: N

Return types restored (D1): N
  sub_401230: __int64 → int (callers assign to int, compare against -1)
  sub_401500: void → int (callers check return value)

Parameter types restored (D2): N
  sub_401230: a1 __int64 → const char * (null-checked, passed to strlen)
  sub_401500: a2 int → size_t (compared against sizeof result)

Parameter names restored (D3): N
  sub_401230: a1 → pwd, a2 → len
  sub_401500: a1 → buf, a2 → buf_len, a3 → flags

Calling conventions fixed (D4): N
  sub_401230: removed __fastcall (redundant on x64)
  sub_402000: __stdcall → __cdecl (variadic function)

Dropped parameters recovered (D5): N
  printLine: recovered 1 parameter (UNINIT_RECOVERED_arg1)

Skipped (insufficient evidence): N
  sub_403000: a3 — ambiguous usage, kept as __int64

Compilation verified: yes / no (gcc exit code)
```
