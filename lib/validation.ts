import { HttpError } from "./auth";
import type { Kind } from "./types";
export function text(value: unknown, max = 200) {
  if (typeof value !== "string") throw new HttpError(400, "문자열 입력이 필요합니다.");
  const result = value.trim();
  if (!result || result.length > max) throw new HttpError(400, `1~${max}자 이내로 입력해 주세요.`);
  return result;
}
export function optionalId(value: unknown): string | null {
  if (value === null || value === "" || value === undefined) return null;
  if (typeof value !== "string" || !/^[0-9a-f-]{36}$/i.test(value)) throw new HttpError(400, "잘못된 ID입니다.");
  return value;
}
export function transactionInput(raw: unknown) {
  const data = raw as Record<string, unknown>;
  const kind = data?.kind;
  if (kind !== "income" && kind !== "expense") throw new HttpError(400, "입금 또는 출금을 선택해 주세요.");
  const date = data.date;
  if (typeof date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(date) || Number.isNaN(Date.parse(date)) || new Date(date).toISOString().slice(0, 10) !== date) throw new HttpError(400, "올바른 회계일자를 입력해 주세요.");
  const amount = Number(data.amount);
  if (!Number.isSafeInteger(amount) || amount <= 0) throw new HttpError(400, "금액은 1원 이상의 정수여야 합니다.");
  return { kind: kind as Kind, date, amount, description: text(data.description, 300), categoryId: optionalId(data.categoryId), memberId: optionalId(data.memberId) };
}
