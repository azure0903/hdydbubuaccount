import { NextResponse } from "next/server";
import { errorResponse, HttpError, requestGroup, requireUser } from "@/lib/auth";
import { ledgerData, saveMetadata, validateMetadata } from "@/lib/ledger";
import { appendTransaction, deleteTransaction, loadTransactions, updateTransaction } from "@/lib/sheets";
import { isSupabaseConfigured } from "@/lib/supabase";
import { optionalId, transactionInput } from "@/lib/validation";
import type { GroupId } from "@/lib/group";
import { createDreamTransaction, deleteDreamTransaction, updateDreamTransaction } from "@/lib/dreamharam";
export const runtime = "nodejs";
async function find(group: GroupId, id: unknown) {
  const validId = optionalId(id);
  if (!validId) throw new HttpError(400, "거래 ID가 필요합니다.");
  const row = (await loadTransactions(group)).find(item => item.id === validId);
  if (!row) throw new HttpError(404, "거래를 찾을 수 없습니다.");
  return row;
}
export async function POST(request: Request) {
  try {
    const group = requestGroup(request); const user = await requireUser(group); const input = transactionInput(await request.json());
    await validateMetadata(group, input.categoryId, input.memberId);
    if (group === "dreamharam") {
      const id = await createDreamTransaction(input, user);
      return NextResponse.json({ id, warning: null }, { status: 201 });
    }
    const id = await appendTransaction(group, input, user);
    let warning: string | null = null;
    if (isSupabaseConfigured()) {
      try { await ledgerData(group); await saveMetadata(group, id, input.categoryId, input.memberId); }
      catch { warning = "Sheet에는 저장되었지만 Supabase 동기화에 실패했습니다. 설정과 테이블을 확인해 주세요."; }
    }
    return NextResponse.json({ id, warning }, { status: 201 });
  } catch (e) { return errorResponse(e); }
}
export async function PUT(request: Request) {
  try {
    const group = requestGroup(request); await requireUser(group); const raw = await request.json(); const input = transactionInput(raw);
    if (group === "dreamharam") {
      const id = optionalId(raw.id); if (!id) throw new HttpError(400, "거래 ID가 필요합니다.");
      await validateMetadata(group, input.categoryId, input.memberId);
      await updateDreamTransaction(id, input);
      return NextResponse.json({ ok: true, warning: null });
    }
    const row = await find(group, raw.id);
    await validateMetadata(group, input.categoryId, input.memberId);
    await updateTransaction(group, row, input);
    let warning: string | null = null;
    if (isSupabaseConfigured()) {
      try { await ledgerData(group); await saveMetadata(group, row.id, input.categoryId, input.memberId); }
      catch { warning = "Sheet는 수정되었지만 Supabase 동기화에 실패했습니다."; }
    }
    return NextResponse.json({ ok: true, warning });
  } catch (e) { return errorResponse(e); }
}
export async function DELETE(request: Request) {
  try {
    const group = requestGroup(request); await requireUser(group); const raw = await request.json();
    if (group === "dreamharam") {
      const id = optionalId(raw.id); if (!id) throw new HttpError(400, "거래 ID가 필요합니다.");
      await deleteDreamTransaction(id);
      return NextResponse.json({ ok: true, warning: null });
    }
    const row = await find(group, raw.id);
    await deleteTransaction(group, row);
    let warning: string | null = null;
    if (isSupabaseConfigured()) { try { await ledgerData(group); } catch { warning = "Sheet에서는 삭제되었지만 Supabase 동기화에 실패했습니다."; } }
    return NextResponse.json({ ok: true, warning });
  } catch (e) { return errorResponse(e); }
}
