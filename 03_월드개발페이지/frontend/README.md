# Cloudflare Compatibility Shim

This folder exists only to support older Cloudflare Pages settings that still point to `03_월드개발페이지/frontend`.

The active project is `000_월드개발페이지`. The build script in this folder delegates to the active project and writes the deployable output into this folder's `dist/` directory.

When Cloudflare Pages is updated to use `000_월드개발페이지/frontend` as the root directory, this compatibility shim can be removed.
