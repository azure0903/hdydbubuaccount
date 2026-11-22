import { createClient } from "@supabase/supabase-js";
import { HttpError } from "./auth";

export function isSupabaseConfigured() { return Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_SECRET_KEY); }
export function db() {
  if (!isSupabaseConfigured()) throw new HttpError(503, "Supabase 환경 변수가 설정되지 않았습니다.");
  return createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SECRET_KEY!, {
    auth: { autoRefreshToken: false, persistSession: false }
  });
}
