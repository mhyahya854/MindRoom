# MindRoom Graphify V2 Report

Run: `mindroom-graphify-forensic-finalization-20260730-150956`  
Nodes: 35274  
Directed parallel-preserving edges: 107213  
Graph health: PASS

## God Nodes (authored runtime only)

- `Codebase/packages/common/graphql/src/schema.ts` — degree 881 (in 2, out 879)
- `Codebase/packages/frontend/apps/ios/src/app.tsx` — degree 468 (in 11, out 457)
- `Codebase/packages/frontend/apps/android/src/app.tsx` — degree 455 (in 11, out 444)
- `Codebase/packages/frontend/apps/mobile/src/app.tsx` — degree 416 (in 8, out 408)
- `Codebase/packages/frontend/apps/web/src/app.tsx` — degree 404 (in 6, out 398)
- `Codebase/packages/frontend/apps/electron-renderer/src/app/app.tsx` — degree 380 (in 1, out 379)
- `Codebase/packages/frontend/apps/ios/src/index.tsx` — degree 361 (in 0, out 361)
- `Codebase/packages/frontend/apps/android/src/index.tsx` — degree 358 (in 0, out 358)
- `Codebase/packages/frontend/apps/electron-renderer/src/shell/app.tsx` — degree 332 (in 2, out 330)
- `Codebase/packages/frontend/core/src/modules/cloud/index.ts` — degree 318 (in 193, out 125)

## Bridge Nodes (authored runtime only)

- `Codebase/packages/frontend/core/src/modules/cloud/index.ts` — bridge score 24125
- `Codebase/packages/frontend/core/src/modules/workspace/index.ts` — bridge score 11178
- `Codebase/blocksuite/framework/std/src/gfx/index.ts` — bridge score 10092
- `Codebase/packages/backend/server/src/base/index.ts` — bridge score 9040
- `Codebase/packages/backend/server/src/native.ts` — bridge score 8178
- `Codebase/packages/backend/server/src/models/index.ts` — bridge score 8051
- `Codebase/packages/frontend/apps/ios/src/app.tsx` — bridge score 5027
- `Codebase/packages/frontend/apps/android/src/app.tsx` — bridge score 4884
- `Codebase/packages/frontend/core/src/modules/workbench/index.ts` — bridge score 4326
- `Codebase/packages/frontend/core/src/modules/storage/index.ts` — bridge score 4074

## Surprising Connections

- `Codebase/packages/frontend/apps/ios/src/index.tsx` —RUNTIME_ENTRYPOINT→ `Codebase/packages/frontend/core/src/components/hooks/affine/use-register-blocksuite-editor-commands.tsx::COMMAND_REGISTRATION::command_registration@L151`
- `Codebase/packages/frontend/apps/electron-renderer/src/shell/app.tsx` —STATIC_IMPORT→ `Codebase/packages/frontend/core/src/modules/i18n/index.ts`
- `Codebase/blocksuite/playground/apps/starter/utils/app.ts` —RUNTIME_ENTRYPOINT→ `Codebase/blocksuite/affine/widgets/edgeless-dragging-area/src/view.ts::DI_REGISTRATION::edgelessDraggingAreaWidget`
- `Codebase/packages/frontend/apps/web/src/app.tsx` —RUNTIME_ENTRYPOINT→ `Codebase/packages/frontend/core/src/commands/affine-settings.tsx::COMMAND_REGISTRATION::command_registration@L174`
- `Codebase/packages/frontend/apps/ios/src/index.tsx` —RUNTIME_ENTRYPOINT→ `Codebase/blocksuite/affine/blocks/code/src/store.ts::DI_REGISTRATION::CodeMarkdownPreprocessorExtension`
- `Codebase/packages/frontend/apps/android/src/app.tsx` —RUNTIME_ENTRYPOINT→ `Codebase/packages/frontend/apps/electron/src/main/windows-manager/tab-views.ts::MENU_REGISTRATION::Menu.buildFromTemplate(`
- `Codebase/blocksuite/affine/blocks/root/src/edgeless/utils/connector.ts` —STATIC_IMPORT→ `Codebase/blocksuite/affine/blocks/surface/src/index.ts`
- `Codebase/packages/frontend/apps/mobile/src/app.tsx` —RUNTIME_ENTRYPOINT→ `Codebase/blocksuite/affine/widgets/viewport-overlay/src/view.ts::DI_REGISTRATION::viewportOverlayWidget`
- `Codebase/packages/frontend/apps/electron-renderer/src/app/app.tsx` —RUNTIME_ENTRYPOINT→ `Codebase/blocksuite/affine/blocks/code/src/store.ts::DI_REGISTRATION::CodeBlockSchemaExtension`
- `Codebase/blocksuite/framework/std/src/inline/extensions/inline-spec.ts::InlineSpecExtension` —FUNCTION_CALL→ `Codebase/blocksuite/framework/global/src/di/container.ts`

## Suggested Questions

- Which authored-runtime bridge has the highest removal blast radius after excluded-system edges are filtered?
- Which mixed runtime registration roots combine retained local behavior with later cloud removal work?
- Which workspace package exports form the most important barrel-to-declaration chains?
- Which migration dependencies constrain future local-first schema changes?
