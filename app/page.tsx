import Link from "next/link";
export default function Home() {
  return <main className="hub"><div className="hub-content"><div className="brand-icon">✦</div><p className="eyebrow">하늘꿈연동교회</p><h1>회계관리</h1><p className="muted">접속할 부서를 선택해 주세요.</p><div className="hub-grid"><Link href="/bubu" className="hub-card"><span className="hub-symbol">♧</span><strong>부부청년부</strong><small>회계 내역 열기 →</small></Link><Link href="/dreamharam" className="hub-card"><span className="hub-symbol">✿</span><strong>꿈하람 유치부</strong><small>회계 내역 열기 →</small></Link></div></div></main>;
}
