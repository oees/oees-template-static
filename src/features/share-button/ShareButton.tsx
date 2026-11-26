import { useState } from "react";

type Status = "idle" | "copied" | "failed";

const MESSAGES: Record<Status, string> = {
  idle: "",
  copied: "Enlace copiado",
  failed: "No se pudo copiar el enlace",
};

type ShareButtonProps = {
  url: string;
  label?: string;
};

export function ShareButton({ url, label = "Copiar enlace" }: ShareButtonProps) {
  const [status, setStatus] = useState<Status>("idle");

  async function copy(): Promise<void> {
    try {
      await navigator.clipboard.writeText(url);
      setStatus("copied");
    } catch {
      // Clipboard access can be refused by the browser; tell the visitor instead of failing silently.
      setStatus("failed");
    }
  }

  return (
    <p>
      <button type="button" onClick={() => void copy()}>
        {label}
      </button>
      <span className="share-button__status" role="status">
        {MESSAGES[status]}
      </span>
    </p>
  );
}
