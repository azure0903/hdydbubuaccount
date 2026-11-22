import { randomUUID } from "node:crypto";
import { google } from "googleapis";
import { HttpError } from "./auth";
import type { Transaction } from "./types";
import { GROUPS, type GroupId } from "./group";

const HEADERS = ["기록일자", "회계일자", "입금", "입금내역", "출금", "출금내역", "작성자", "거래ID"];
function sheetId(group: GroupId) { const id = process.env[GROUPS[group].sheetEnv]; if (!id) throw new HttpError(503, `${GROUPS[group].name} Google Sheet ID가 설정되지 않았습니다.`); return id; }
async function client() {
  const encoded = process.env.GOOGLE_SERVICE_ACCOUNT_B64;
  if (!encoded) throw new Error("GOOGLE_SERVICE_ACCOUNT_B64이 필요합니다.");
  const credentials = JSON.parse(Buffer.from(encoded, "base64").toString("utf8"));
  const auth = new google.auth.GoogleAuth({ credentials, scopes: ["https://www.googleapis.com/auth/spreadsheets"] });
  return google.sheets({ version: "v4", auth });
}
function asAmount(value: unknown): number { const n = Number(String(value ?? 0).replaceAll(",", "")); return Number.isFinite(n) ? Math.max(0, n) : 0; }
function dateOnly(value: unknown) { return String(value ?? "").slice(0, 10); }
export async function loadTransactions(group: GroupId): Promise<Transaction[]> {
  const sheets = await client(); const spreadsheetId = sheetId(group);
  const result = await sheets.spreadsheets.values.get({ spreadsheetId, range: "A:H", valueRenderOption: "FORMATTED_VALUE" });
  const rows = result.data.values ?? [];
  if (rows.length && HEADERS.slice(0, 7).some((header, i) => rows[0]?.[i] !== header)) throw new Error("Google Sheet의 A:G 헤더가 기존 형식과 다릅니다.");
  if (!rows.length) await sheets.spreadsheets.values.update({ spreadsheetId, range: "A1:H1", valueInputOption: "RAW", requestBody: { values: [HEADERS] } });
  else if (rows[0]?.[7] !== HEADERS[7]) await sheets.spreadsheets.values.update({ spreadsheetId, range: "H1", valueInputOption: "RAW", requestBody: { values: [[HEADERS[7]]] } });
  const updates: { range: string; values: string[][] }[] = [];
  const records = rows.slice(1).flatMap((row, index) => {
    if (!row.some(cell => String(cell ?? "").trim())) return [];
    const id = row[7] && /^[0-9a-f-]{36}$/i.test(String(row[7])) ? String(row[7]) : randomUUID();
    if (id !== row[7]) updates.push({ range: `H${index + 2}`, values: [[id]] });
    const income = asAmount(row[2]); const expense = asAmount(row[4]);
    return [{ id, sheetRow: index + 2, recordedAt: String(row[0] ?? ""), date: dateOnly(row[1]), kind: expense > 0 ? "expense" : "income", amount: expense > 0 ? expense : income, description: String(expense > 0 ? row[5] ?? "" : row[3] ?? ""), writer: String(row[6] ?? ""), categoryId: null, memberId: null } satisfies Transaction];
  });
  if (updates.length) await sheets.spreadsheets.values.batchUpdate({ spreadsheetId, requestBody: { valueInputOption: "RAW", data: updates } });
  return records;
}
export async function appendTransaction(group: GroupId, input: Pick<Transaction, "date" | "kind" | "amount" | "description">, writer: string) {
  const sheets = await client(); const spreadsheetId = sheetId(group); const id = randomUUID();
  const recordedAt = new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Seoul", dateStyle: "short", timeStyle: "medium" }).format(new Date());
  const values = [[recordedAt, input.date, input.kind === "income" ? input.amount : 0, input.kind === "income" ? input.description : "", input.kind === "expense" ? input.amount : 0, input.kind === "expense" ? input.description : "", writer, id]];
  await sheets.spreadsheets.values.append({ spreadsheetId, range: "A:H", valueInputOption: "RAW", insertDataOption: "INSERT_ROWS", requestBody: { values } });
  return id;
}
export async function updateTransaction(group: GroupId, existing: Transaction, input: Pick<Transaction, "date" | "kind" | "amount" | "description">) {
  const sheets = await client();
  await sheets.spreadsheets.values.update({ spreadsheetId: sheetId(group), range: `A${existing.sheetRow}:H${existing.sheetRow}`, valueInputOption: "RAW", requestBody: { values: [[existing.recordedAt, input.date, input.kind === "income" ? input.amount : 0, input.kind === "income" ? input.description : "", input.kind === "expense" ? input.amount : 0, input.kind === "expense" ? input.description : "", existing.writer, existing.id]] } });
}
export async function deleteTransaction(group: GroupId, existing: Transaction) {
  const sheets = await client(); const spreadsheetId = sheetId(group);
  const meta = await sheets.spreadsheets.get({ spreadsheetId, fields: "sheets(properties(sheetId,title))" });
  const firstSheetId = meta.data.sheets?.[0]?.properties?.sheetId;
  if (firstSheetId == null) throw new HttpError(500, "첫 번째 시트를 찾을 수 없습니다.");
  await sheets.spreadsheets.batchUpdate({ spreadsheetId, requestBody: { requests: [{ deleteDimension: { range: { sheetId: firstSheetId, dimension: "ROWS", startIndex: existing.sheetRow - 1, endIndex: existing.sheetRow } } }] } });
}
