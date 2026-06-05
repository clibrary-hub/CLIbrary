# Contentstack with Gatsby

Complete patterns for Gatsby with Contentstack source plugin and Live Preview.

## Installation

```bash
npm install gatsby-source-contentstack @contentstack/live-preview-utils
```

## Plugin Configuration

```javascript
// gatsby-config.js
module.exports = {
  plugins: [
    {
      resolve: "gatsby-source-contentstack",
      options: {
        api_key: process.env.CONTENTSTACK_API_KEY,
        delivery_token: process.env.CONTENTSTACK_DELIVERY_TOKEN,
        environment: process.env.CONTENTSTACK_ENVIRONMENT,
        // Optional: for Live Preview
        live_preview: {
          enable: true,
          preview_token: process.env.CONTENTSTACK_PREVIEW_TOKEN,
          host: "rest-preview.contentstack.com",
        },
      },
    },
  ],
};
```

## Environment Variables

```bash
# .env.development
CONTENTSTACK_API_KEY=your_api_key
CONTENTSTACK_DELIVERY_TOKEN=your_delivery_token
CONTENTSTACK_PREVIEW_TOKEN=your_preview_token
CONTENTSTACK_ENVIRONMENT=preview
```

---

## Live Preview Setup

### Create Live Preview Helper

```javascript
// src/live-preview.js
import { ContentstackGatsby } from "gatsby-source-contentstack/live-preview";

export const cs = new ContentstackGatsby({
  api_key: process.env.GATSBY_CONTENTSTACK_API_KEY,
  environment: process.env.GATSBY_CONTENTSTACK_ENVIRONMENT,
  live_preview: {
    enable: true,
    preview_token: process.env.GATSBY_CONTENTSTACK_PREVIEW_TOKEN,
    host: "rest-preview.contentstack.com",
  },
});
```

### Initialize in gatsby-browser.js

```javascript
// gatsby-browser.js
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import { cs } from "./src/live-preview";

export const onClientEntry = () => {
  ContentstackLivePreview.init({
    enable: true,
    ssr: false,
    stackSdk: cs.stackSdk,
    stackDetails: {
      apiKey: process.env.GATSBY_CONTENTSTACK_API_KEY,
      environment: process.env.GATSBY_CONTENTSTACK_ENVIRONMENT,
    },
    editButton: { enable: true },
  });
};
```

---

## Page Component with Live Preview

```jsx
// src/pages/index.js
import React, { useState, useEffect } from "react";
import { graphql } from "gatsby";
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import { addEditableTags } from "@contentstack/utils";
import { cs } from "../live-preview";

export const query = graphql`
  query HomePageQuery {
    contentstackPage(url: { eq: "/" }) {
      uid
      title
      description
      url
    }
  }
`;

const HomePage = ({ data }) => {
  const [page, setPage] = useState(data.contentstackPage);

  useEffect(() => {
    // Fetch updated data on live edit
    const fetchUpdated = async () => {
      const updated = await cs.get(data.contentstackPage);
      addEditableTags(updated, "page", false, "en-us");
      setPage(updated);
    };

    ContentstackLivePreview.onLiveEdit(fetchUpdated);
  }, [data.contentstackPage]);

  // Add editable tags on initial render
  useEffect(() => {
    addEditableTags(page, "page", false, "en-us");
  }, []);

  return (
    <main>
      <h1 data-cslp={page.$?.title?.["data-cslp"]}>{page.title}</h1>
      <p data-cslp={page.$?.description?.["data-cslp"]}>{page.description}</p>
    </main>
  );
};

export default HomePage;
```

---

## GraphQL Queries

### Basic Page Query

```graphql
query PageQuery($url: String!) {
  contentstackPage(url: { eq: $url }) {
    uid
    title
    url
    description
    featured_image {
      url
      title
    }
  }
}
```

### Blog Posts with References

```graphql
query BlogPostsQuery {
  allContentstackBlogPost(
    sort: { published_date: DESC }
    limit: 10
  ) {
    nodes {
      uid
      title
      url
      excerpt
      published_date
      author {
        uid
        name
        avatar {
          url
        }
      }
    }
  }
}
```

### With Modular Blocks

```graphql
query PageWithBlocksQuery($url: String!) {
  contentstackPage(url: { eq: $url }) {
    uid
    title
    blocks {
      ... on ContentstackPageBlocksHeroBlock {
        hero_block {
          title
          description
          image {
            url
          }
        }
      }
      ... on ContentstackPageBlocksContentBlock {
        content_block {
          title
          content
        }
      }
    }
  }
}
```

---

## Dynamic Page Creation

```javascript
// gatsby-node.js
exports.createPages = async ({ graphql, actions }) => {
  const { createPage } = actions;

  const result = await graphql(`
    query {
      allContentstackPage {
        nodes {
          uid
          url
        }
      }
    }
  `);

  result.data.allContentstackPage.nodes.forEach((page) => {
    createPage({
      path: page.url,
      component: require.resolve("./src/templates/page.js"),
      context: {
        uid: page.uid,
        url: page.url,
      },
    });
  });
};
```

### Page Template

```jsx
// src/templates/page.js
import React, { useState, useEffect } from "react";
import { graphql } from "gatsby";
import ContentstackLivePreview from "@contentstack/live-preview-utils";
import { addEditableTags } from "@contentstack/utils";
import { cs } from "../live-preview";

export const query = graphql`
  query PageTemplateQuery($url: String!) {
    contentstackPage(url: { eq: $url }) {
      uid
      title
      url
      description
    }
  }
`;

const PageTemplate = ({ data }) => {
  const [page, setPage] = useState(data.contentstackPage);

  useEffect(() => {
    const fetchUpdated = async () => {
      const updated = await cs.get(data.contentstackPage);
      addEditableTags(updated, "page", false);
      setPage(updated);
    };

    ContentstackLivePreview.onLiveEdit(fetchUpdated);
    addEditableTags(page, "page", false);
  }, [data.contentstackPage]);

  return (
    <main>
      <h1 data-cslp={page.$?.title?.["data-cslp"]}>{page.title}</h1>
      <p data-cslp={page.$?.description?.["data-cslp"]}>{page.description}</p>
    </main>
  );
};

export default PageTemplate;
```

---

## Modular Blocks Component

```jsx
// src/components/BlockRenderer.js
import React from "react";
import HeroBlock from "./blocks/HeroBlock";
import ContentBlock from "./blocks/ContentBlock";
import CTABlock from "./blocks/CTABlock";

const blockComponents = {
  hero_block: HeroBlock,
  content_block: ContentBlock,
  cta_block: CTABlock,
};

const BlockRenderer = ({ blocks }) => {
  if (!blocks) return null;

  return (
    <>
      {blocks.map((blockItem, index) => {
        // Gatsby returns blocks in different format
        const blockKey = Object.keys(blockItem).find(
          (key) => key !== "__typename"
        );
        const block = blockItem[blockKey];
        const Component = blockComponents[blockKey];

        if (!Component) return null;

        return <Component key={index} block={block} />;
      })}
    </>
  );
};

export default BlockRenderer;
```

---

## Image Handling

```jsx
// src/components/ContentstackImage.js
import React from "react";
import { GatsbyImage, getImage } from "gatsby-plugin-image";

const ContentstackImage = ({ asset, width, height, className }) => {
  // If Gatsby image data available
  if (asset.gatsbyImageData) {
    return (
      <GatsbyImage
        image={getImage(asset)}
        alt={asset.title || asset.filename}
        className={className}
      />
    );
  }

  // Fallback to URL with transformations
  const params = new URLSearchParams();
  if (width) params.append("width", width);
  if (height) params.append("height", height);

  const src = params.toString()
    ? `${asset.url}?${params.toString()}`
    : asset.url;

  return (
    <img
      src={src}
      alt={asset.title || asset.filename}
      width={width}
      height={height}
      className={className}
    />
  );
};

export default ContentstackImage;
```

---

## Important Notes

### Edit Tags in Gatsby

Gatsby uses string-based edit tags (not object-based like React):

```jsx
// Gatsby style
<h1 data-cslp={page.$?.title?.["data-cslp"]}>{page.title}</h1>

// Not like React style
// <h1 {...page.$.title}>{page.title}</h1>
```

### Using addEditableTags

```javascript
import { addEditableTags } from "@contentstack/utils";

// For Gatsby (HTML strings) - use false
addEditableTags(entry, "content_type_uid", false, "en-us");

// For React/JSX (objects) - use true
addEditableTags(entry, "content_type_uid", true, "en-us");
```

### onLiveEdit vs onEntryChange

- `onLiveEdit` - Only fires when actively editing (recommended for Gatsby)
- `onEntryChange` - Fires on any entry change

---

## Troubleshooting

### Build Errors

Ensure environment variables are prefixed with `GATSBY_` for client-side access:

```bash
GATSBY_CONTENTSTACK_API_KEY=your_key
```

### Preview Not Updating

1. Check `cs.get()` is being called with correct entry
2. Verify `onLiveEdit` handler is registered
3. Ensure preview token is valid

### GraphQL Schema Errors

Run `gatsby clean` and restart dev server after content model changes.

