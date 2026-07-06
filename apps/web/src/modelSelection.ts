export type SelectableModel = {
  id: string;
};

export const DIRECTML_SAFE_DEFAULT_SIZE = 768;

export function chooseSelectedModel(current: string, installed: SelectableModel[]): string {
  if (installed.some((model) => model.id === current)) {
    return current;
  }
  return installed[0]?.id ?? "";
}

export function directmlLabel(value: "ready" | "convert" | "experimental"): string {
  if (value === "ready") return "compatible";
  if (value === "convert") return "convertir";
  return "experimental";
}
