import { NextResponse } from "next/server";
import { errorResponse, HttpError, requestGroup, requireUser } from "@/lib/auth";
import { db } from "@/lib/supabase";
import { optionalId, text } from "@/lib/validation";
export const runtime = "nodejs";
export async function POST(request: Request) {
  try { const group = requestGroup(request); await requireUser(group); const raw = await request.json(); const name = text(raw.name, 80); const note = typeof raw.note === "string" ? raw.note.trim().slice(0, 300) : "";
    const { data, error } = await db().from("members").insert({ group_id: group, name, note, active: true }).select().single(); if (error) throw error; return NextResponse.json(data, { status: 201 });
  } catch (e) { return errorResponse(e); }
}
export async function PATCH(request: Request) {
  try { const group = requestGroup(request); await requireUser(group); const raw = await request.json(); const id = optionalId(raw.id); if (!id) throw new HttpError(400, "ID가 필요합니다.");
    const name = text(raw.name, 80); const note = typeof raw.note === "string" ? raw.note.trim().slice(0, 300) : "";
    const { error } = await db().from("members").update({ name, note, active: raw.active !== false }).eq("group_id", group).eq("id", id); if (error) throw error; return NextResponse.json({ ok: true });
  } catch (e) { return errorResponse(e); }
}
export async function DELETE(request: Request) {
  try { const group = requestGroup(request); await requireUser(group); const { id: rawId } = await request.json(); const id = optionalId(rawId); if (!id) throw new HttpError(400, "ID가 필요합니다.");
    const { error } = await db().from("members").delete().eq("group_id", group).eq("id", id); if (error) throw error; return NextResponse.json({ ok: true });
  } catch (e) { return errorResponse(e); }
}
