export type GroupId = "bubu" | "dreamharam";

export const GROUPS: Record<GroupId, { name: string; sheetEnv: string }> = {
  bubu: { name: "부부청년부", sheetEnv: "GOOGLE_SHEET_ID" },
  dreamharam: { name: "꿈하람 유치부", sheetEnv: "DREAMHARAM_GOOGLE_SHEET_ID" }
};

export function parseGroup(value: unknown): GroupId | null {
  return value === "bubu" || value === "dreamharam" ? value : null;
}

export function isSheetConfigured(group: GroupId) {
  return Boolean(process.env[GROUPS[group].sheetEnv]);
}
