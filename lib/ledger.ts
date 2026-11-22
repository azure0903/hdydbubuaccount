import { db, isSupabaseConfigured } from "./supabase";
import { loadTransactions } from "./sheets";
import type { Category, Member, Transaction } from "./types";
import { isSheetConfigured, type GroupId } from "./group";
import { HttpError } from "./auth";

export async function ledgerData(group: GroupId) {
  const sheetConfigured = isSheetConfigured(group);
  const transactions = sheetConfigured ? await loadTransactions(group) : [];
  if (!isSupabaseConfigured()) return { transactions, categories: [] as Category[], members: [] as Member[], supabaseConfigured: false, sheetConfigured };
  const supabase = db();
  const [mirrorResult, categoryResult, memberResult] = await Promise.all([
    supabase.from("transactions").select("id,category_id,member_id").eq("group_id", group),
    supabase.from("categories").select("id,name,kind,color").eq("group_id", group).order("name"),
    supabase.from("members").select("id,name,note,active").eq("group_id", group).order("name")
  ]);
  for (const result of [mirrorResult, categoryResult, memberResult]) if (result.error) throw result.error;
  const mirror = new Map((mirrorResult.data ?? []).map(row => [row.id as string, row]));
  const merged = transactions.map(row => ({ ...row, categoryId: mirror.get(row.id)?.category_id ?? null, memberId: mirror.get(row.id)?.member_id ?? null }));
  const updates = merged.map(row => ({
    id: row.id, group_id: group, sheet_row: row.sheetRow, recorded_at: row.recordedAt, accounting_date: row.date,
    kind: row.kind, amount: row.amount, description: row.description, writer: row.writer,
    category_id: row.categoryId, member_id: row.memberId
  }));
  if (updates.length) {
    const { error } = await supabase.from("transactions").upsert(updates, { onConflict: "id" });
    if (error) throw error;
  }
  const liveIds = new Set(merged.map(row => row.id));
  const stale = sheetConfigured ? (mirrorResult.data ?? []).map(row => row.id as string).filter(id => !liveIds.has(id)) : [];
  if (stale.length) {
    const { error } = await supabase.from("transactions").delete().eq("group_id", group).in("id", stale);
    if (error) throw error;
  }
  return { transactions: merged, categories: (categoryResult.data ?? []) as Category[], members: (memberResult.data ?? []) as Member[], supabaseConfigured: true, sheetConfigured };
}
export async function validateMetadata(group: GroupId, categoryId: string | null, memberId: string | null) {
  if (!categoryId && !memberId) return;
  if (!isSupabaseConfigured()) throw new HttpError(503, "카테고리와 명단을 사용하려면 Supabase 연결이 필요합니다.");
  const supabase = db();
  if (categoryId) {
    const { data, error } = await supabase.from("categories").select("id").eq("group_id", group).eq("id", categoryId).maybeSingle();
    if (error) throw error;
    if (!data) throw new HttpError(400, "다른 부서의 카테고리를 사용할 수 없습니다.");
  }
  if (memberId) {
    const { data, error } = await supabase.from("members").select("id").eq("group_id", group).eq("id", memberId).maybeSingle();
    if (error) throw error;
    if (!data) throw new HttpError(400, "다른 부서의 명단을 사용할 수 없습니다.");
  }
}
export async function saveMetadata(group: GroupId, id: string, categoryId: string | null, memberId: string | null) {
  if (!isSupabaseConfigured()) return;
  await validateMetadata(group, categoryId, memberId);
  const supabase = db();
  const { error } = await supabase.from("transactions").update({ category_id: categoryId, member_id: memberId }).eq("group_id", group).eq("id", id);
  if (error) throw error;
}
