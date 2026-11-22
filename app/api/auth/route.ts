import { NextResponse } from "next/server";
import { clearSession, currentUser, errorResponse, HttpError, requestGroup, setSession, verifyLogin } from "@/lib/auth";
export const runtime = "nodejs";
export async function GET(request: Request) { try { const group = requestGroup(request); return NextResponse.json({ user: await currentUser(group) }); } catch (e) { return errorResponse(e); } }
export async function POST(request: Request) {
  try {
    const group = requestGroup(request);
    const { username, password } = await request.json();
    if (typeof username !== "string" || typeof password !== "string" || !verifyLogin(username, password, group)) throw new HttpError(401, "아이디 또는 비밀번호가 올바르지 않습니다.");
    const response = NextResponse.json({ user: username }); setSession(response, username, group); return response;
  } catch (e) { return errorResponse(e); }
}
export async function DELETE(request: Request) { try { const group = requestGroup(request); const response = NextResponse.json({ ok: true }); clearSession(response, group); return response; } catch (e) { return errorResponse(e); } }
