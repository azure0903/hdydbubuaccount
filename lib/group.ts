export type GroupId = "bubu" | "dreamharam";

export const GROUPS: Record<GroupId, { name: string }> = {
  bubu: { name: "부부청년부" },
  dreamharam: { name: "꿈하람 유치부" }
};

export function parseGroup(value: unknown): GroupId | null {
  return value === "bubu" || value === "dreamharam" ? value : null;
}

export function isSheetConfigured(group: GroupId) {
  return group === "bubu" && Boolean(process.env.GOOGLE_SHEET_ID);
}
