import { createHash, createHmac, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { parseGroup, type GroupId } from "./group";

const cookieName = (group: GroupId) => `account_session_${group}`;
const WEEK = 60 * 60 * 24 * 7;
function secret() {
  const value = process.env.SESSION_SECRET;
  if (!value || value.length < 32) throw new Error("SESSION_SECRET이 필요합니다.");
  return value;
}
function sign(payload: string) { return createHmac("sha256", secret()).update(payload).digest("base64url"); }
export function requestGroup(request: Request): GroupId {
  const group = parseGroup(new URL(request.url).searchParams.get("group"));
  if (!group) throw new HttpError(400, "올바른 부서 경로가 필요합니다.");
  return group;
}
export function verifyLogin(username: string, password: string, group: GroupId): boolean {
  const encoded = (group === "dreamharam" && process.env.DREAMHARAM_USERS_B64) || process.env.APP_USERS_B64;
  if (!encoded) throw new Error("APP_USERS_B64이 필요합니다.");
  const users = JSON.parse(Buffer.from(encoded, "base64").toString("utf8")) as Record<string, { password_hash: string }>;
  const saved = users[username]?.password_hash;
  if (!saved || !/^[a-f0-9]{64}$/i.test(saved)) return false;
  const actual = createHash("sha256").update(password).digest();
  return timingSafeEqual(actual, Buffer.from(saved, "hex"));
}
export function setSession(response: NextResponse, username: string, group: GroupId) {
  const payload = Buffer.from(JSON.stringify({ username, group, exp: Date.now() + WEEK * 1000 })).toString("base64url");
  response.cookies.set(cookieName(group), `${payload}.${sign(payload)}`, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: WEEK });
}
export function clearSession(response: NextResponse, group: GroupId) { response.cookies.delete(cookieName(group)); }
export async function currentUser(group: GroupId): Promise<string | null> {
  const value = (await cookies()).get(cookieName(group))?.value;
  if (!value) return null;
  const [payload, signature] = value.split(".");
  if (!payload || !signature) return null;
  const expected = sign(payload);
  if (signature.length !== expected.length || !timingSafeEqual(Buffer.from(signature), Buffer.from(expected))) return null;
  try {
    const parsed = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    return typeof parsed.username === "string" && parsed.group === group && parsed.exp > Date.now() ? parsed.username : null;
  } catch { return null; }
}
export async function requireUser(group: GroupId) {
  const user = await currentUser(group);
  if (!user) throw new HttpError(401, "로그인이 필요합니다.");
  return user;
}
export class HttpError extends Error { constructor(public status: number, message: string) { super(message); } }
export function errorResponse(error: unknown) {
  const status = error instanceof HttpError ? error.status : 500;
  const message = error instanceof Error ? error.message : "요청을 처리하지 못했습니다.";
  console.error("API error:", message);
  return NextResponse.json({ error: message }, { status });
}
