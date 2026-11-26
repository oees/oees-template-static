import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ShareButton } from "./ShareButton";

describe("ShareButton", () => {
  it("copies the url and confirms it to the visitor", async () => {
    const user = userEvent.setup();
    render(<ShareButton url="https://example.com/pagina/" />);

    await user.click(screen.getByRole("button", { name: "Copiar enlace" }));

    expect(await navigator.clipboard.readText()).toBe("https://example.com/pagina/");
    expect(screen.getByRole("status")).toHaveTextContent("Enlace copiado");
  });

  it("tells the visitor when the browser refuses the clipboard", async () => {
    const user = userEvent.setup();
    vi.spyOn(navigator.clipboard, "writeText").mockRejectedValue(new Error("denied"));
    render(<ShareButton url="https://example.com/" />);

    await user.click(screen.getByRole("button", { name: "Copiar enlace" }));

    expect(screen.getByRole("status")).toHaveTextContent("No se pudo copiar el enlace");
  });
});
