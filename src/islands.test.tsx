import { screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { mountIslands } from "./islands";

describe("mountIslands", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("mounts a registered island into its element", async () => {
    document.body.innerHTML = '<div data-island="share-button"></div>';

    mountIslands(document);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Copiar enlace" })).toBeInTheDocument();
    });
  });

  it("reports an unknown island instead of failing silently", () => {
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    document.body.innerHTML = '<div data-island="does-not-exist"></div>';

    mountIslands(document);

    expect(error).toHaveBeenCalledWith(expect.stringContaining('"does-not-exist"'));
  });
});
