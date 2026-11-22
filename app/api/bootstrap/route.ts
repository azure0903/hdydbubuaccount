import { NextResponse } from "next/server";
import { errorResponse, requestGroup, requireUser } from "@/lib/auth";
import { ledgerData } from "@/lib/ledger";
export const runtime = "nodejs";
export async function GET(request: Request) { try { const group = requestGroup(request); const user = await requireUser(group); return NextResponse.json({ user, ...await ledgerData(group) }); } catch (e) { return errorResponse(e); } }
