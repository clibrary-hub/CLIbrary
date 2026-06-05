# Contentstack OAuth with Auth.js v5 (NextAuth)

A clean, production-ready integration pattern for Contentstack OAuth with Auth.js v5 in Next.js applications. Includes critical lessons learned from deploying to serverless environments (Vercel, Contentstack Launch).

---

## Quick Reference (for AI Agents)

**Files to create:**

1. `lib/auth.ts` — Auth.js configuration with Contentstack provider
2. `app/api/auth/[...nextauth]/route.ts` — Route handler

**Required packages:**

```bash
npm install next-auth@5 @timbenniks/contentstack-endpoints
```

**Required environment variables:**

- `AUTH_SECRET` — Random string for JWT encryption
- `AUTH_TRUST_HOST=true` — Required for serverless deployments (Vercel, Contentstack Launch)
- `CONTENTSTACK_REGION` — Region code (na, eu, azure-na, azure-eu, gcp-na, gcp-eu)
- `CONTENTSTACK_APP_ID` — App UID from Developer Hub
- `CONTENTSTACK_CLIENT_ID` — OAuth client ID
- `CONTENTSTACK_CLIENT_SECRET` — OAuth client secret
- `NEXTAUTH_URL` — App URL for callbacks (use HTTPS for production)

**Contentstack setup:**

- Redirect URL: `{NEXTAUTH_URL}/api/auth/callback/contentstack`
- Required scope: `user:read` (add CMA scopes as needed)

**Critical implementation details:**

- Authorization URL: `{appUrl}/apps/{APP_ID}/authorize` — NOT `#!/apps/...`
- Token URL: `{appUrl}/apps-api/token`
- Userinfo URL: `{apiUrl}/v3/user` — response is nested under `user` key
- Use `checks: ["state"]` (or `["pkce", "state"]` for PKCE)
- Always use `session: { strategy: "jwt" }`
- On serverless: use `auth()` for session/token access — never `getToken()` without `secureCookie`
- Auth route handler must export `dynamic = "force-dynamic"`

---

## Prerequisites

- Next.js 14+ with App Router
- Auth.js v5 (`next-auth@5`)
- A Contentstack app with OAuth enabled in Developer Hub

## Environment Variables

```env
# Auth.js secret (generate with: openssl rand -base64 32)
AUTH_SECRET="your-secret"

# Required for serverless deployments (Vercel, Contentstack Launch)
AUTH_TRUST_HOST=true

# Contentstack OAuth (from Developer Hub > Your App > OAuth)
CONTENTSTACK_REGION="eu"          # na, eu, azure-na, azure-eu, gcp-na, gcp-eu
CONTENTSTACK_APP_ID="your-app-uid"
CONTENTSTACK_CLIENT_ID="your-client-id"
CONTENTSTACK_CLIENT_SECRET="your-client-secret"

# App URL (for OAuth callbacks)
# IMPORTANT: Use HTTPS for production/serverless deployments
NEXTAUTH_URL="http://localhost:3000"
```

### Environment Variable Notes

- **`AUTH_SECRET`** is the v5 name. Auth.js also reads `NEXTAUTH_SECRET` as a fallback.
- **`AUTH_TRUST_HOST=true`** tells Auth.js to trust the `Host` / `X-Forwarded-Host` headers. Required when running behind a reverse proxy or on serverless platforms.
- **`NEXTAUTH_URL`** must use `https://` in production. On Vercel, Auth.js auto-detects the URL via `VERCEL_URL`, but setting it explicitly avoids edge cases.
- Do not set both `AUTH_URL` and `NEXTAUTH_URL` to different values — Auth.js v5 prefers `AUTH_URL` when both are present.

## Contentstack App Configuration

In Contentstack Developer Hub → Your App → OAuth:

1. **Redirect URL**: `{NEXTAUTH_URL}/api/auth/callback/contentstack`
2. **User Token Scopes**: Select the scopes your app needs. At minimum: `user:read`

Common scope combinations:

| Use case | Scopes |
|----------|--------|
| Read-only | `user:read` |
| CMS authoring | `user:read cm.content-types.management:read cm.entries.management:read cm.entries.management:write cm.assets.management:read cm.assets.management:write` |
| CMS + taxonomies | Add: `cm.taxonomies.management:read cm.taxonomies.management:write cm.taxonomy.terms:read cm.taxonomy.terms:write` |
| Full management | All available scopes |

## Installation

```bash
npm install next-auth@5 @timbenniks/contentstack-endpoints
```

---

## Option 1: Cookie-Based Sessions (Recommended)

The simplest approach — no database required. User sessions are stored as encrypted JWTs in HTTP-only cookies.

### Auth Configuration

**File: `lib/auth.ts`**

```typescript
import NextAuth from "next-auth";
import type { JWT } from "next-auth/jwt";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

const region = process.env.CONTENTSTACK_REGION ?? "na";
const endpoints = getContentstackEndpoints(region);
const appUrl = endpoints.application!;
const apiUrl = endpoints.contentManagement!;

type ContentstackProfile = {
  uid: string;
  email: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  profile_image?: string;
};

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: { strategy: "jwt" },
  pages: { signIn: "/login", error: "/login" },

  providers: [
    {
      id: "contentstack",
      name: "Contentstack",
      type: "oauth",
      checks: ["state"],
      authorization: {
        url: `${appUrl}/apps/${process.env.CONTENTSTACK_APP_ID}/authorize`,
        params: { response_type: "code", scope: "user:read" },
      },
      token: `${appUrl}/apps-api/token`,
      userinfo: {
        url: `${apiUrl}/v3/user`,
        async request({
          tokens,
        }: {
          tokens: { access_token?: string };
        }) {
          const res = await fetch(`${apiUrl}/v3/user`, {
            headers: {
              Authorization: `Bearer ${tokens.access_token ?? ""}`,
            },
          });
          const { user } = (await res.json()) as {
            user: ContentstackProfile;
          };
          return user;
        },
      },
      profile: (profile: ContentstackProfile) => ({
        id: profile.uid,
        name:
          [profile.first_name, profile.last_name]
            .filter(Boolean)
            .join(" ") ||
          profile.username ||
          profile.email,
        email: profile.email,
        image: profile.profile_image ?? null,
      }),
      clientId: process.env.CONTENTSTACK_CLIENT_ID,
      clientSecret: process.env.CONTENTSTACK_CLIENT_SECRET,
    },
  ],

  callbacks: {
    jwt({ token, user }) {
      if (user) token.sub = user.id;
      return token;
    },
    session({ session, token }) {
      if (token.sub) session.user.id = token.sub;
      return session;
    },
  },
});
```

### Route Handler

**File: `app/api/auth/[...nextauth]/route.ts`**

```typescript
import { handlers } from "@/lib/auth";

export const dynamic = "force-dynamic";

export const { GET, POST } = handlers;
```

> **`export const dynamic = "force-dynamic"` is critical.** Without it, serverless platforms may statically optimize or cache this route, breaking the OAuth callback flow.

That's it for basic auth! No database setup required.

---

## Storing the Contentstack Access Token (CMA Access)

If your app needs to call the Contentstack Content Management API on behalf of the user, you must persist the OAuth access token and refresh token in the JWT.

### Extended Auth Configuration with Token Storage

**File: `lib/auth.ts`**

```typescript
import NextAuth from "next-auth";
import type { JWT } from "next-auth/jwt";
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";
import { redirect } from "next/navigation";

const region = process.env.CONTENTSTACK_REGION ?? "na";
const endpoints = getContentstackEndpoints(region);
const appUrl = endpoints.application!;
const apiUrl = endpoints.contentManagement!;

type ContentstackProfile = {
  uid: string;
  email: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  profile_image?: string;
};

type ExtendedToken = JWT & {
  accessToken?: string;
  refreshToken?: string;
  accessTokenExpiresAt?: number;
  error?: "RefreshAccessTokenError";
};

async function refreshAccessToken(
  token: ExtendedToken
): Promise<ExtendedToken> {
  try {
    const body = new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: token.refreshToken ?? "",
      client_id: process.env.CONTENTSTACK_CLIENT_ID ?? "",
      client_secret: process.env.CONTENTSTACK_CLIENT_SECRET ?? "",
    });

    const res = await fetch(`${appUrl}/apps-api/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!res.ok) {
      return { ...token, error: "RefreshAccessTokenError" };
    }

    const data = await res.json();

    return {
      ...token,
      accessToken: data.access_token ?? token.accessToken,
      refreshToken: data.refresh_token ?? token.refreshToken,
      accessTokenExpiresAt: data.expires_in
        ? Date.now() + data.expires_in * 1000
        : token.accessTokenExpiresAt,
      error: undefined,
    };
  } catch {
    return { ...token, error: "RefreshAccessTokenError" };
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  session: { strategy: "jwt" },
  pages: { signIn: "/login", error: "/login" },

  providers: [
    {
      id: "contentstack",
      name: "Contentstack",
      type: "oauth",
      checks: ["state"],
      authorization: {
        url: `${appUrl}/apps/${process.env.CONTENTSTACK_APP_ID}/authorize`,
        params: {
          response_type: "code",
          scope:
            "user:read cm.content-types.management:read cm.entries.management:read cm.entries.management:write cm.assets.management:read cm.assets.management:write cm.taxonomies.management:read cm.taxonomies.management:write cm.taxonomy.terms:read cm.taxonomy.terms:write",
        },
      },
      token: `${appUrl}/apps-api/token`,
      userinfo: {
        url: `${apiUrl}/v3/user`,
        async request({
          tokens,
        }: {
          tokens: { access_token?: string };
        }) {
          const res = await fetch(`${apiUrl}/v3/user`, {
            headers: {
              Authorization: `Bearer ${tokens.access_token ?? ""}`,
            },
          });
          const { user } = (await res.json()) as {
            user: ContentstackProfile;
          };
          return user;
        },
      },
      profile: (profile: ContentstackProfile) => ({
        id: profile.uid,
        name:
          [profile.first_name, profile.last_name]
            .filter(Boolean)
            .join(" ") ||
          profile.username ||
          profile.email,
        email: profile.email,
        image: profile.profile_image ?? null,
      }),
      clientId: process.env.CONTENTSTACK_CLIENT_ID,
      clientSecret: process.env.CONTENTSTACK_CLIENT_SECRET,
    },
  ],

  callbacks: {
    async jwt({ token, user, account }) {
      // Initial sign-in: persist the OAuth tokens
      if (user && account) {
        const expiresAt =
          typeof account.expires_at === "number"
            ? account.expires_at
            : typeof account.expires_at === "string"
              ? Number(account.expires_at)
              : undefined;
        const expiresIn =
          typeof account.expires_in === "number"
            ? account.expires_in
            : typeof account.expires_in === "string"
              ? Number(account.expires_in)
              : undefined;

        return {
          ...token,
          sub: user.id,
          name: user.name ?? null,
          email: user.email ?? null,
          picture: user.image ?? null,
          accessToken: account.access_token,
          refreshToken: account.refresh_token,
          accessTokenExpiresAt: Number.isFinite(expiresAt)
            ? expiresAt! * 1000
            : Number.isFinite(expiresIn)
              ? Date.now() + expiresIn! * 1000
              : undefined,
        } as ExtendedToken;
      }

      // Subsequent requests: check if token needs refresh
      const current = token as ExtendedToken;
      const safetyWindowMs = 60_000; // refresh 60s before expiry

      if (
        current.accessToken &&
        (!current.accessTokenExpiresAt ||
          Date.now() < current.accessTokenExpiresAt - safetyWindowMs)
      ) {
        return current; // token still valid
      }

      if (current.refreshToken) {
        return refreshAccessToken(current);
      }

      // No refresh token available
      return {
        ...current,
        accessToken: undefined,
        refreshToken: undefined,
        accessTokenExpiresAt: undefined,
        error: "RefreshAccessTokenError",
      };
    },

    session({ session, token }) {
      const ext = token as ExtendedToken;
      if (ext.sub) {
        session.user.id = ext.sub;
        session.user.name = ext.name ?? session.user.name;
        session.user.email = ext.email ?? session.user.email;
        session.user.image = ext.picture ?? session.user.image;
      }
      // Expose the access token to server components
      session.accessToken = ext.accessToken;
      session.error = ext.error;
      return session;
    },
  },
});

// Helper: require authenticated session or redirect to login
export async function requireSession() {
  const session = await auth();
  if (!session) redirect("/login");
  return session;
}
```

### Type Augmentation

**File: `types/next-auth.d.ts`**

```typescript
import "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    error?: "RefreshAccessTokenError";
  }
}
```

### Using the Access Token in Server Components

```typescript
import { requireSession } from "@/lib/auth";

export default async function DashboardPage() {
  const session = await requireSession();

  // Use session.accessToken to call Contentstack CMA
  const res = await fetch("https://eu-api.contentstack.com/v3/content_types", {
    headers: {
      api_key: process.env.CONTENTSTACK_API_KEY!,
      authorization: `Bearer ${session.accessToken}`,
    },
  });

  const data = await res.json();
  // ...
}
```

---

## Option 2: Database-Persisted Sessions

Use this approach if you need to:

- Store additional user data
- Track user activity
- Link users to other models in your database
- Revoke sessions server-side

### Additional Installation

```bash
npm install @auth/prisma-adapter @prisma/client prisma
```

### Prisma Schema

**File: `prisma/schema.prisma`**

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"  // or "postgresql", "mysql"
  url      = env("DATABASE_URL")
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?
  user              User    @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String?   @unique
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}
```

### Database Client

**File: `lib/db.ts`**

```typescript
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const db = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = db;
```

### Auth Configuration with Prisma

Add the adapter to any of the auth configurations above:

```typescript
import { PrismaAdapter } from "@auth/prisma-adapter";
import { db } from "./db";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(db),
  session: { strategy: "jwt" }, // Still use JWT strategy
  // ... rest of config
});
```

### Initialize Database

```bash
npx prisma db push
```

---

## Usage Patterns

### Server Component

```typescript
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function ProtectedPage() {
  const session = await auth();
  if (!session) redirect("/login");

  return <div>Welcome, {session.user.name}</div>;
}
```

### Client Component (Sign In)

```typescript
"use client";
import { signIn } from "next-auth/react";

export function SignInButton() {
  return (
    <button
      onClick={() => signIn("contentstack", { callbackUrl: "/dashboard" })}
    >
      Sign in with Contentstack
    </button>
  );
}
```

### Server Action (Sign In)

```typescript
import { signIn } from "@/lib/auth";

export default function LoginPage() {
  return (
    <form
      action={async () => {
        "use server";
        await signIn("contentstack", { redirectTo: "/dashboard" });
      }}
    >
      <button type="submit">Sign in with Contentstack</button>
    </form>
  );
}
```

### Middleware (Route Protection)

**File: `middleware.ts`** (project root)

```typescript
export { auth as middleware } from "@/lib/auth";

export const config = {
  matcher: ["/dashboard/:path*", "/app/:path*"],
};
```

---

## Serverless Deployment: Critical Gotchas

Deploying to Vercel, Contentstack Launch, or any serverless platform introduces issues that don't exist in local development. This section documents confirmed bugs and their fixes.

### 1. The `__Secure-` Cookie Prefix Problem

**Symptom**: Auth works locally but returns "Missing access token" on production, even though cookies are clearly set in the browser.

**Root cause**: On HTTPS, Auth.js sets the session cookie as `__Secure-authjs.session-token` (with the `__Secure-` prefix). But if you use `getToken()` from `next-auth/jwt` without passing `secureCookie: true`, it defaults to looking for `authjs.session-token` (no prefix). The cookie names don't match, so the token is never found.

**How Auth.js decides the cookie name:**

| Context | Cookie name |
|---------|-------------|
| HTTP (localhost) | `authjs.session-token` |
| HTTPS (production) | `__Secure-authjs.session-token` |

The auth handler detects the protocol from the request URL. But `getToken()` is a standalone helper — it has no request context and defaults to the non-secure name unless you tell it otherwise.

**Fix**: Don't use `getToken()` directly. Use `auth()` instead, which handles cookie name detection internally:

```typescript
// BAD: getToken() without secureCookie — breaks on HTTPS
import { getToken } from "next-auth/jwt";
import { cookies } from "next/headers";

async function getAccessToken() {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore
    .getAll()
    .map(({ name, value }) => `${name}=${value}`)
    .join("; ");

  const token = await getToken({
    req: { headers: { cookie: cookieHeader } },
    secret: process.env.AUTH_SECRET,
    // Missing secureCookie! Defaults to false → looks for wrong cookie name on HTTPS
  });

  return token?.accessToken;
}
```

```typescript
// GOOD: Use auth() which handles secure cookies automatically
import { auth } from "@/lib/auth";

async function getAccessToken() {
  const session = await auth();
  return session?.accessToken;
}
```

If you absolutely must use `getToken()` (e.g., in diagnostic tooling), always pass `secureCookie`:

```typescript
import { getToken } from "next-auth/jwt";

const isSecure =
  process.env.NODE_ENV === "production" ||
  (process.env.AUTH_URL ?? process.env.NEXTAUTH_URL ?? "").startsWith("https");

const token = await getToken({
  req: { headers: { cookie: cookieHeader } },
  secret: process.env.AUTH_SECRET,
  secureCookie: isSecure,
});
```

### 2. Auth Route Must Be Dynamic

**Symptom**: OAuth callback returns errors or stale responses on serverless.

**Fix**: Always mark the auth route handler as dynamic:

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/lib/auth";

export const dynamic = "force-dynamic";

export const { GET, POST } = handlers;
```

Without this, serverless platforms may statically optimize or cache the route, breaking the stateful OAuth redirect flow.

### 3. `AUTH_TRUST_HOST` Is Required

**Symptom**: Auth callbacks fail with URL mismatch or redirect errors on serverless.

**Fix**: Set `AUTH_TRUST_HOST=true` in your production environment variables. This tells Auth.js to trust the `Host` and `X-Forwarded-Host` headers, which are set by reverse proxies on Vercel and Contentstack Launch.

### 4. Don't Duplicate Token Refresh Logic

The JWT callback in Auth.js already handles token refresh on every `auth()` call. If you also implement manual refresh logic elsewhere (e.g., in your CMA client), you'll have two competing refresh paths that can cause race conditions.

**Pattern**: Let the JWT callback own all token refresh logic. Server components and server actions should simply read `session.accessToken` from `auth()`:

```typescript
// The JWT callback handles refresh automatically
const session = await requireSession();
if (!session.accessToken) {
  // Token refresh failed — redirect to login
  redirect("/login");
}
// Use session.accessToken for CMA calls
```

### 5. Environment Variable Checklist for Production

| Variable | Required | Notes |
|----------|----------|-------|
| `AUTH_SECRET` | Yes | `openssl rand -base64 32` |
| `AUTH_TRUST_HOST` | Yes (serverless) | Set to `true` |
| `NEXTAUTH_URL` | Recommended | Must be `https://` for production |
| `CONTENTSTACK_APP_ID` | Yes | From Developer Hub |
| `CONTENTSTACK_CLIENT_ID` | Yes | From Developer Hub > OAuth |
| `CONTENTSTACK_CLIENT_SECRET` | Yes | From Developer Hub > OAuth |
| `CONTENTSTACK_REGION` | Yes | Determines API endpoints |

---

## URL Construction (Important!)

The authorization URL format is **critical** and easy to get wrong.

### Correct Format

```
Authorization: {appUrl}/apps/{APP_ID}/authorize
Token:         {appUrl}/apps-api/token
Userinfo:      {apiUrl}/v3/user
```

### Common Mistakes

```
❌ {appUrl}/#!/apps/{APP_ID}/authorize     # Hash routing doesn't work
❌ {appUrl}/apps/authorize                  # Missing APP_ID
❌ {appUrl}/apps/{CLIENT_ID}/authorize      # Wrong ID (use APP_ID, not CLIENT_ID)
```

### URL Resolution with @timbenniks/contentstack-endpoints

```typescript
import { getContentstackEndpoints } from "@timbenniks/contentstack-endpoints";

const endpoints = getContentstackEndpoints("eu");

// endpoints.application       → "https://eu-app.contentstack.com"
// endpoints.contentManagement → "https://eu-api.contentstack.com"
```

### Full URL Examples (EU Region)

| Endpoint | URL |
|----------|-----|
| Authorization | `https://eu-app.contentstack.com/apps/{APP_ID}/authorize` |
| Token | `https://eu-app.contentstack.com/apps-api/token` |
| Userinfo | `https://eu-api.contentstack.com/v3/user` |
| Callback | `https://your-app.vercel.app/api/auth/callback/contentstack` |

---

## Key Points

| Aspect | Detail |
|--------|--------|
| **PKCE support** | Contentstack supports PKCE — see note below |
| **Custom userinfo** | Contentstack returns data nested under `user` key |
| **Region URLs** | Use `@timbenniks/contentstack-endpoints` for correct endpoints |
| **JWT required** | Always use `session: { strategy: "jwt" }` |
| **Serverless** | Use `auth()` not `getToken()` — set `AUTH_TRUST_HOST=true` — mark auth route as dynamic |

### PKCE (Proof Key for Code Exchange)

Contentstack supports [PKCE](https://www.contentstack.com/docs/developers/developer-hub/pkce-for-contentstack-oauth) for enhanced security. This example uses `checks: ["state"]` for simplicity, but you can enable PKCE:

```typescript
{
  id: "contentstack",
  type: "oauth",
  checks: ["pkce", "state"],  // Enable PKCE
  // ... rest of config
}
```

PKCE is recommended for:

- Public clients (SPAs, mobile apps)
- Enhanced protection against authorization code interception attacks

For server-side Next.js apps with a client secret, `checks: ["state"]` is sufficient.

## Contentstack Profile Fields

The userinfo endpoint returns:

```typescript
interface ContentstackUser {
  uid: string;
  email: string;
  first_name?: string;
  last_name?: string;
  username?: string;
  profile_image?: string;
}
```

## Debugging Auth Issues

When auth fails on production, check these in order:

1. **Browser DevTools → Application → Cookies**: Is the session cookie present? What's its name (`authjs.session-token` vs `__Secure-authjs.session-token`)?
2. **Environment variables**: Is `AUTH_SECRET` set? Is `AUTH_TRUST_HOST=true`? Is `NEXTAUTH_URL` using `https://`?
3. **Network tab**: Does the `/api/auth/callback/contentstack` request succeed? Check for redirect loops or error responses.
4. **Server logs**: Look for `"RefreshAccessTokenError"` — this means the refresh token is expired or invalid, and the user needs to re-authenticate.

### Diagnostic Report Pattern

For production debugging, you can build a diagnostic report that checks cookie state and token readability:

```typescript
import { cookies } from "next/headers";
import { getToken } from "next-auth/jwt";

export async function buildAuthDiagnostics() {
  const cookieStore = await cookies();
  const cookieNames = cookieStore.getAll().map((c) => c.name);

  const sessionCookieName = [
    "__Secure-authjs.session-token",
    "authjs.session-token",
  ].find((name) => cookieNames.includes(name));

  const isSecure =
    process.env.NODE_ENV === "production" ||
    (process.env.AUTH_URL ?? process.env.NEXTAUTH_URL ?? "").startsWith("https");

  const cookieHeader = cookieStore
    .getAll()
    .map(({ name, value }) => `${name}=${value}`)
    .join("; ");

  let tokenReadable = false;
  try {
    const token = await getToken({
      req: { headers: { cookie: cookieHeader } },
      secret: process.env.AUTH_SECRET ?? process.env.NEXTAUTH_SECRET,
      secureCookie: isSecure,
    });
    tokenReadable = Boolean(token);
  } catch {}

  return {
    sessionCookieName: sessionCookieName ?? "none",
    isSecure,
    tokenReadable,
    authTrustHost: process.env.AUTH_TRUST_HOST ?? "unset",
    authSecretSet: Boolean(process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET),
  };
}
```

## References

- [Contentstack OAuth Documentation](https://www.contentstack.com/docs/developers/developer-hub/contentstack-oauth)
- [Contentstack PKCE Documentation](https://www.contentstack.com/docs/developers/developer-hub/pkce-for-contentstack-oauth)
- [Auth.js v5 Documentation](https://authjs.dev)
- [Auth.js v5 Migration Guide](https://authjs.dev/getting-started/migrating-to-v5)
- [@timbenniks/contentstack-endpoints](https://www.npmjs.com/package/@timbenniks/contentstack-endpoints)
