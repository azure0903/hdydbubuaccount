import { randomUUID } from "node:crypto";
import { HttpError } from "./auth";
import { db } from "./supabase";
import type { Transaction } from "./types";

type Input = Pick<Transaction, "date" | "kind" | "amount" | "description" | "categoryId" | "memberId">;

export async function createDreamTransaction(input: Input, writer: string) {
  const id = randomUUID();
  const { error } = await db().from("transactions").insert({
    id, group_id: "dreamharam", recorded_at: new Date().toISOString(),
    accounting_date: input.date, kind: input.kind, amount: input.amount,
    description: input.description, writer, category_id: input.categoryId, member_id: input.memberId
  });
  if (error) throw error;
  return id;
}

export async function updateDreamTransaction(id: string, input: Input) {
  const { data, error } = await db().from("transactions").update({
    accounting_date: input.date, kind: input.kind, amount: input.amount,
    description: input.description, category_id: input.categoryId, member_id: input.memberId,
    updated_at: new Date().toISOString()
  }).eq("group_id", "dreamharam").eq("id", id).select("id").maybeSingle();
  if (error) throw error;
  if (!data) throw new HttpError(404, "거래를 찾을 수 없습니다.");
}

export async function deleteDreamTransaction(id: string) {
  const { data, error } = await db().from("transactions").delete().eq("group_id", "dreamharam").eq("id", id).select("id").maybeSingle();
  if (error) throw error;
  if (!data) throw new HttpError(404, "거래를 찾을 수 없습니다.");
}
