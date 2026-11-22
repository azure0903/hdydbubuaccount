"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { Category, Kind, Member, Transaction } from "@/lib/types";
import { GROUPS, type GroupId } from "@/lib/group";

type Boot = { user: string; transactions: Transaction[]; categories: Category[]; members: Member[]; supabaseConfigured: boolean; sheetConfigured: boolean };
type Entry = { date: string; kind: Kind; amount: string; description: string; categoryId: string; memberId: string };
const today = () => new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Seoul" });
const emptyEntry = (): Entry => ({ date: today(), kind: "income", amount: "", description: "", categoryId: "", memberId: "" });
const money = (n: number) => `₩${n.toLocaleString("ko-KR")}`;
async function api(path: string, method = "GET", body?: unknown) {
  const response = await fetch(path, { method, headers: body ? { "Content-Type": "application/json" } : undefined, body: body ? JSON.stringify(body) : undefined, cache: "no-store" });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "요청을 처리하지 못했습니다.");
  return result;
}
function csvCell(value: unknown) {
  const string = String(value ?? "");
  const safe = /^[=+\-@]/.test(string) ? `'${string}` : string;
  return `"${safe.replaceAll('"', '""')}"`;
}
function downloadCsv(rows: Transaction[], categories: Category[], members: Member[]) {
  const headers = ["기록일자", "회계일자", "입금", "입금내역", "출금", "출금내역", "작성자", "카테고리", "명단", "거래ID"];
  const values = rows.map(row => [row.recordedAt, row.date, row.kind === "income" ? row.amount : 0, row.kind === "income" ? row.description : "", row.kind === "expense" ? row.amount : 0, row.kind === "expense" ? row.description : "", row.writer, categories.find(c => c.id === row.categoryId)?.name ?? "", members.find(m => m.id === row.memberId)?.name ?? "", row.id]);
  const csv = "\ufeff" + [headers, ...values].map(row => row.map(csvCell).join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a"); link.href = url; link.download = `회계내역_${today()}.csv`; link.click(); URL.revokeObjectURL(url);
}
export default function AccountingApp({ group }: { group: GroupId }) {
  const groupName = GROUPS[group].name;
  const scoped = (path: string) => `${path}?group=${group}`;
  const [boot, setBoot] = useState<Boot | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [tab, setTab] = useState<"ledger" | "categories" | "members">("ledger");
  const [entry, setEntry] = useState<Entry>(emptyEntry);
  const [editId, setEditId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [month, setMonth] = useState("");
  const [kindFilter, setKindFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [memberFilter, setMemberFilter] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [categoryKind, setCategoryKind] = useState<"income" | "expense" | "both">("both");
  const [categoryColor, setCategoryColor] = useState("#4472c4");
  const [categoryEditId, setCategoryEditId] = useState<string | null>(null);
  const [memberName, setMemberName] = useState("");
  const [memberNote, setMemberNote] = useState("");
  const [memberActive, setMemberActive] = useState(true);
  const [memberEditId, setMemberEditId] = useState<string | null>(null);
  const reload = useCallback(async () => { const data = await api(scoped("/api/bootstrap")) as Boot; setBoot(data); }, [group]);
  useEffect(() => { api(scoped("/api/auth")).then(async data => { if (data.user) await reload(); }).catch(e => setError(e.message)).finally(() => setAuthChecked(true)); }, [reload]);
  const run = async (action: () => Promise<void>) => { setLoading(true); setError(""); setNotice(""); try { await action(); } catch (e) { setError(e instanceof Error ? e.message : "오류가 발생했습니다."); } finally { setLoading(false); } };
  const filtered = useMemo(() => {
    if (!boot) return [];
    return [...boot.transactions].filter(row =>
      (!month || row.date.startsWith(month)) && (!kindFilter || row.kind === kindFilter) &&
      (!categoryFilter || row.categoryId === categoryFilter) && (!memberFilter || row.memberId === memberFilter) &&
      (!search || `${row.description} ${row.writer} ${boot.members.find(m => m.id === row.memberId)?.name ?? ""}`.toLowerCase().includes(search.toLowerCase()))
    ).sort((a, b) => b.date.localeCompare(a.date) || b.sheetRow - a.sheetRow);
  }, [boot, month, kindFilter, categoryFilter, memberFilter, search]);
  const totals = useMemo(() => {
    const income = filtered.filter(r => r.kind === "income").reduce((sum, r) => sum + r.amount, 0);
    const expense = filtered.filter(r => r.kind === "expense").reduce((sum, r) => sum + r.amount, 0);
    return { income, expense, balance: income - expense };
  }, [filtered]);
  const resetEntry = () => { setEntry(emptyEntry()); setEditId(null); };
  const startEdit = (row: Transaction) => { setEntry({ date: row.date, kind: row.kind, amount: String(row.amount), description: row.description, categoryId: row.categoryId ?? "", memberId: row.memberId ?? "" }); setEditId(row.id); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const saveEntry = (event: React.FormEvent) => { event.preventDefault(); run(async () => {
    const result = await api(scoped("/api/transactions"), editId ? "PUT" : "POST", { ...entry, amount: Number(entry.amount), id: editId, categoryId: entry.categoryId || null, memberId: entry.memberId || null });
    resetEntry(); await reload(); setNotice(result.warning || (editId ? "거래를 수정했습니다." : "거래를 저장했습니다."));
  }); };
  const removeEntry = (row: Transaction) => { if (!window.confirm(`${row.date} ${row.description} 거래를 삭제할까요?`)) return; run(async () => { const result = await api(scoped("/api/transactions"), "DELETE", { id: row.id }); await reload(); setNotice(result.warning || "거래를 삭제했습니다."); }); };
  const saveCategory = (event: React.FormEvent) => { event.preventDefault(); run(async () => { await api(scoped("/api/categories"), categoryEditId ? "PATCH" : "POST", { id: categoryEditId, name: categoryName, kind: categoryKind, color: categoryColor }); setCategoryName(""); setCategoryKind("both"); setCategoryColor("#4472c4"); setCategoryEditId(null); await reload(); setNotice("카테고리를 저장했습니다."); }); };
  const saveMember = (event: React.FormEvent) => { event.preventDefault(); run(async () => { await api(scoped("/api/members"), memberEditId ? "PATCH" : "POST", { id: memberEditId, name: memberName, note: memberNote, active: memberActive }); setMemberName(""); setMemberNote(""); setMemberActive(true); setMemberEditId(null); await reload(); setNotice("명단을 저장했습니다."); }); };
  if (!authChecked) return <main className="center"><p>불러오는 중...</p></main>;
  if (!boot) return <main className="login-page"><section className="login-card"><div className="brand-icon">✦</div><p className="eyebrow">하늘꿈연동교회 · {groupName}</p><h1>회계관리</h1><p className="muted">회계 내역을 안전하게 정리하고 확인하세요.</p><form onSubmit={event => { event.preventDefault(); run(async () => { await api(scoped("/api/auth"), "POST", { username, password }); setPassword(""); await reload(); }); }}><label>아이디<input value={username} onChange={e => setUsername(e.target.value)} required autoComplete="username" /></label><label>비밀번호<input type="password" value={password} onChange={e => setPassword(e.target.value)} required autoComplete="current-password" /></label>{error && <p className="alert error">{error}</p>}<button className="primary full" disabled={loading}>{loading ? "확인 중..." : "로그인"}</button></form></section></main>;
  return <main className="shell">
    <header className="topbar"><div className="logo-mark">✦</div><div className="top-title"><strong>{groupName} 회계관리</strong><span>하늘꿈연동교회</span></div><div className="top-spacer"/><a className="text-button" href="/">부서 선택</a><span className="user-chip">{boot.user}님</span><button className="text-button" onClick={() => run(async () => { await api(scoped("/api/auth"), "DELETE"); setBoot(null); })}>로그아웃</button></header>
    <div className="content"><div className="page-heading"><div><p className="eyebrow">ACCOUNTING WORKSPACE</p><h1>회계 현황</h1><p className="muted">수입과 지출, 구성원별 내역을 한곳에서 관리하세요.</p></div><button className="outline" onClick={() => downloadCsv(filtered, boot.categories, boot.members)}>↓ CSV 다운로드</button></div>
      {!boot.sheetConfigured && <div className="alert info">{groupName} Google Sheet가 아직 연결되지 않았습니다. Sheet를 만든 뒤 환경 변수에 ID를 입력하면 거래를 사용할 수 있습니다.</div>}
      {!boot.supabaseConfigured && <div className="alert info">Supabase 연결 전입니다. 카테고리와 명단 관리는 연결 후 사용할 수 있습니다.</div>}
      {error && <div className="alert error" role="alert">{error}</div>}{notice && <div className="alert success" role="status">{notice}</div>}
      <nav className="tabs" aria-label="관리 메뉴"><button className={tab === "ledger" ? "active" : ""} onClick={() => setTab("ledger")}>회계 내역</button><button className={tab === "categories" ? "active" : ""} onClick={() => setTab("categories")}>카테고리 설정</button><button className={tab === "members" ? "active" : ""} onClick={() => setTab("members")}>명단 관리</button></nav>
      {tab === "ledger" && <><div className="metrics"><div className="metric"><span>총 입금</span><strong className="income">{money(totals.income)}</strong><small>현재 필터 기준</small></div><div className="metric"><span>총 출금</span><strong className="expense">{money(totals.expense)}</strong><small>현재 필터 기준</small></div><div className="metric"><span>잔액</span><strong>{money(totals.balance)}</strong><small>입금 − 출금</small></div></div>
        <div className="grid"><section className="panel entry-panel"><div className="section-heading"><div><p className="eyebrow">NEW ENTRY</p><h2>{editId ? "회계 내역 수정" : "회계 내역 입력"}</h2></div>{editId && <button className="text-button" onClick={resetEntry}>취소</button>}</div><form onSubmit={saveEntry}><div className="segmented" role="group" aria-label="입출금 선택"><button type="button" className={entry.kind === "income" ? "selected" : ""} onClick={() => setEntry({ ...entry, kind: "income", categoryId: "" })}>＋ 입금</button><button type="button" className={entry.kind === "expense" ? "selected expense-choice" : ""} onClick={() => setEntry({ ...entry, kind: "expense", categoryId: "" })}>－ 출금</button></div><label>회계일자<input type="date" value={entry.date} onChange={e => setEntry({ ...entry, date: e.target.value })} required /></label><label>금액 (원)<input type="number" min="1" step="1" placeholder="0" value={entry.amount} onChange={e => setEntry({ ...entry, amount: e.target.value })} required /></label><label>내역<input maxLength={300} placeholder="예: 주일 헌금, 모임 식대" value={entry.description} onChange={e => setEntry({ ...entry, description: e.target.value })} required /></label><label>카테고리<select value={entry.categoryId} onChange={e => setEntry({ ...entry, categoryId: e.target.value })} disabled={!boot.supabaseConfigured}><option value="">선택 안 함</option>{boot.categories.filter(c => c.kind === "both" || c.kind === entry.kind).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label><label>관련 명단<select value={entry.memberId} onChange={e => setEntry({ ...entry, memberId: e.target.value })} disabled={!boot.supabaseConfigured}><option value="">선택 안 함</option>{boot.members.filter(m => m.active || m.id === entry.memberId).map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select></label><button className="primary full" disabled={loading || !boot.sheetConfigured}>{loading ? "저장 중..." : editId ? "수정 저장" : "내역 저장"}</button></form></section>
          <section className="panel table-panel"><div className="section-heading"><div><p className="eyebrow">TRANSACTIONS</p><h2>거래 내역 <span className="count">{filtered.length}</span></h2></div></div><div className="filters"><input aria-label="내역 검색" placeholder="내역, 작성자, 이름 검색" value={search} onChange={e => setSearch(e.target.value)} /><input aria-label="월 필터" type="month" value={month} onChange={e => setMonth(e.target.value)} /><select aria-label="입출금 필터" value={kindFilter} onChange={e => setKindFilter(e.target.value)}><option value="">전체 유형</option><option value="income">입금</option><option value="expense">출금</option></select><select aria-label="카테고리 필터" value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}><option value="">전체 카테고리</option>{boot.categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select><select aria-label="명단 필터" value={memberFilter} onChange={e => setMemberFilter(e.target.value)}><option value="">전체 명단</option>{boot.members.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select></div><div className="table-wrap"><table><thead><tr><th>회계일자 / 내역</th><th>카테고리 · 명단</th><th>작성자</th><th className="right">금액</th><th>관리</th></tr></thead><tbody>{filtered.map(row => <tr key={row.id}><td><strong>{row.description}</strong><small>{row.date}</small></td><td><div className="badges">{row.categoryId && <span className="badge" style={{ borderColor: boot.categories.find(c => c.id === row.categoryId)?.color }}>{boot.categories.find(c => c.id === row.categoryId)?.name ?? "카테고리"}</span>}{row.memberId && <span className="badge neutral">{boot.members.find(m => m.id === row.memberId)?.name ?? "명단"}</span>}</div></td><td>{row.writer}</td><td className={`right amount ${row.kind}`}>{row.kind === "income" ? "+" : "−"}{money(row.amount)}</td><td><div className="row-actions"><button onClick={() => startEdit(row)}>수정</button><button onClick={() => removeEntry(row)} disabled={loading}>삭제</button></div></td></tr>)}</tbody></table>{filtered.length === 0 && <div className="empty">표시할 회계 내역이 없습니다.</div>}</div></section></div></>}
      {tab === "categories" && <div className="settings-grid"><section className="panel"><div className="section-heading"><div><p className="eyebrow">CATEGORIES</p><h2>{categoryEditId ? "카테고리 수정" : "카테고리 추가"}</h2></div></div><form onSubmit={saveCategory}><label>이름<input value={categoryName} onChange={e => setCategoryName(e.target.value)} maxLength={60} required placeholder="예: 헌금, 모임비" /></label><label>유형<select value={categoryKind} onChange={e => setCategoryKind(e.target.value as typeof categoryKind)}><option value="both">입금·출금 공통</option><option value="income">입금</option><option value="expense">출금</option></select></label><label>표시 색상<input type="color" value={categoryColor} onChange={e => setCategoryColor(e.target.value)} /></label><button className="primary full" disabled={loading || !boot.supabaseConfigured}>저장</button>{categoryEditId && <button type="button" className="outline full" onClick={() => { setCategoryEditId(null); setCategoryName(""); }}>취소</button>}</form></section><section className="panel"><div className="section-heading"><h2>등록된 카테고리</h2></div>{boot.categories.length === 0 && <div className="empty">등록된 카테고리가 없습니다.</div>}{boot.categories.map(c => <div className="setting-row" key={c.id}><span className="color-dot" style={{ background: c.color }} /><div><strong>{c.name}</strong><small>{c.kind === "both" ? "공통" : c.kind === "income" ? "입금" : "출금"}</small></div><div className="top-spacer"/><button className="text-button" onClick={() => { setCategoryEditId(c.id); setCategoryName(c.name); setCategoryKind(c.kind); setCategoryColor(c.color); }}>수정</button><button className="text-button danger" onClick={() => { if (window.confirm(`${c.name} 카테고리를 삭제할까요?`)) run(async () => { await api(scoped("/api/categories"), "DELETE", { id: c.id }); await reload(); }); }}>삭제</button></div>)}</section></div>}
      {tab === "members" && <div className="settings-grid"><section className="panel"><div className="section-heading"><div><p className="eyebrow">PEOPLE</p><h2>{memberEditId ? "명단 수정" : "명단 추가"}</h2></div></div><form onSubmit={saveMember}><label>이름<input value={memberName} onChange={e => setMemberName(e.target.value)} maxLength={80} required placeholder="이름" /></label><label>메모<input value={memberNote} onChange={e => setMemberNote(e.target.value)} maxLength={300} placeholder="선택 사항" /></label>{memberEditId && <label className="checkbox"><input type="checkbox" checked={memberActive} onChange={e => setMemberActive(e.target.checked)} />활성 명단</label>}<button className="primary full" disabled={loading || !boot.supabaseConfigured}>저장</button>{memberEditId && <button type="button" className="outline full" onClick={() => { setMemberEditId(null); setMemberName(""); setMemberNote(""); setMemberActive(true); }}>취소</button>}</form></section><section className="panel"><div className="section-heading"><h2>등록된 명단 <span className="count">{boot.members.length}</span></h2></div>{boot.members.length === 0 && <div className="empty">등록된 명단이 없습니다.</div>}{boot.members.map(m => <div className="setting-row" key={m.id}><span className="avatar">{m.name.slice(0, 1)}</span><div><strong>{m.name} {!m.active && <em>비활성</em>}</strong><small>{m.note || "메모 없음"}</small></div><div className="top-spacer"/><button className="text-button" onClick={() => { setMemberEditId(m.id); setMemberName(m.name); setMemberNote(m.note); setMemberActive(m.active); }}>수정</button><button className="text-button danger" onClick={() => { if (window.confirm(`${m.name}님을 명단에서 삭제할까요?`)) run(async () => { await api(scoped("/api/members"), "DELETE", { id: m.id }); await reload(); }); }}>삭제</button></div>)}</section></div>}
    </div></main>;
}
