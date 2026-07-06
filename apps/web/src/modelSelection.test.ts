import { describe, expect, it } from "vitest";
import { DIRECTML_SAFE_DEFAULT_SIZE, chooseSelectedModel, directmlLabel } from "./modelSelection";

describe("chooseSelectedModel", () => {
  it("keeps the current model when it still exists", () => {
    expect(chooseSelectedModel("b", [{ id: "a" }, { id: "b" }])).toBe("b");
  });

  it("selects the first installed model when current is empty or stale", () => {
    expect(chooseSelectedModel("", [{ id: "a" }])).toBe("a");
    expect(chooseSelectedModel("missing", [{ id: "a" }])).toBe("a");
  });
});

describe("directmlLabel", () => {
  it("does not call compatibility installed-ready", () => {
    expect(directmlLabel("ready")).toBe("compatible");
  });
});

describe("DIRECTML_SAFE_DEFAULT_SIZE", () => {
  it("defaults generation to a safer DirectML resolution", () => {
    expect(DIRECTML_SAFE_DEFAULT_SIZE).toBe(768);
  });
});
