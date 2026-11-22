import { NextResponse } from "next/server";
import { errorResponse, HttpError, requestGroup, requireUser } from "@/lib/auth";
import { db } from "@/lib/supabase";
import { optionalId, text } from "@/lib/validation";
export const runtime = "nodejs";
export async function POST(request: Request) {
  try {
    const group = requestGroup(request); await requireUser(group); const raw = await request.json(); const name = text(raw.name, 60);
    if (!["income", "expense", "both"].includes(raw.kind)) throw new HttpError(400, "카테고리 종류가 올바르지 않습니다.");
    const color = typeof raw.color === "string" && /^#[0-9a-f]{6}$/i.test(raw.color) ? raw.color : "#4472c4";
    const { data, error } = await db().from("categories").insert({ group_id: group, name, kind: raw.kind, color }).select().single();
    if (error) throw error; return NextResponse.json(data, { status: 201 });
  } catch (e) { return errorResponse(e); }
}
export async function PATCH(request: Request) {
  try {
    const group = requestGroup(request); await requireUser(group); const raw = await request.json(); const id = optionalId(raw.id); if (!id) throw new HttpError(400, "ID가 필요합니다.");
    const name = text(raw.name, 60); if (!["income", "expense", "both"].includes(raw.kind)) throw new HttpError(400, "카테고리 종류가 올바르지 않습니다.");
    const color = typeof raw.color === "string" && /^#[0-9a-f]{6}$/i.test(raw.color) ? raw.color : "#4472c4";
    const { error } = await db().from("categories").update({ name, kind: raw.kind, color }).eq("group_id", group).eq("id", id); if (error) throw error;
    return NextResponse.json({ ok: true });
  } catch (e) { return errorResponse(e); }
}
export async function DELETE(request: Request) {
  try { const group = requestGroup(request); await requireUser(group); const { id: rawId } = await request.json(); const id = optionalId(rawId); if (!id) throw new HttpError(400, "ID가 필요합니다.");
    const { error } = await db().from("categories").delete().eq("group_id", group).eq("id", id); if (error) throw error; return NextResponse.json({ ok: true });
  } catch (e) { return errorResponse(e); }
}
