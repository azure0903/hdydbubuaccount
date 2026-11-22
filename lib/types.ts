export type Kind = "income" | "expense";
export type Transaction = {
  id: string; sheetRow: number; recordedAt: string; date: string;
  kind: Kind; amount: number; description: string; writer: string;
  categoryId: string | null; memberId: string | null;
};
export type Category = { id: string; name: string; kind: Kind | "both"; color: string };
export type Member = { id: string; name: string; note: string; active: boolean };
