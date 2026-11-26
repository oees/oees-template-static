import type { ReactElement } from "react";
import { createRoot } from "react-dom/client";

import { ShareButton } from "./features/share-button/ShareButton";

// Interactive parts of a page ("islands"). The page content stays in the HTML; React mounts only
// into elements marked <div data-island="name">. Register each new island here.
const ISLANDS: Record<string, (element: HTMLElement) => ReactElement> = {
  "share-button": () => <ShareButton url={window.location.href} />,
};

export function mountIslands(root: ParentNode): void {
  for (const element of root.querySelectorAll<HTMLElement>("[data-island]")) {
    const name = element.dataset["island"] ?? "";
    const render = ISLANDS[name];
    if (render === undefined) {
      console.error(`Unknown island "${name}". Register it in src/islands.tsx.`);
      continue;
    }
    createRoot(element).render(render(element));
  }
}
