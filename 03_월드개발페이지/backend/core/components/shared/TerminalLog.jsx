import React, { memo } from 'react';

const PIPELINE_STEPS = ['역분석', '글생성', '이미지생성', '평가', '발행', '완료'];

/**
 * 자동화 파이프라인 실시간 터미널 로그 UI.
 * 스텝 진행 표시 + 로그 출력 + 자동 스크롤.
 */
const TerminalLog = memo(function TerminalLog({
  logs,
  terminalStep,
  terminalEndRef,
  height = 'h-[520px]',
}) {
  return (
    <section className={`glass-card rounded-3xl border border-white/5 p-5 shadow-2xl flex flex-col ${height}`}>
      <div className="flex items-center justify-between mb-3.5 shrink-0 border-b border-slate-900 pb-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            자동화 파이프라인 실시간 터미널 로그
          </h3>
        </div>
        <div className="flex gap-1.5">
          {PIPELINE_STEPS.map(step => (
            <span
              key={step}
              className={`text-[11px] px-1.5 py-0.5 rounded-md font-bold uppercase transition-all ${terminalStep === step ? 'bg-indigo-600 text-white font-extrabold scale-110 shadow-md' : 'bg-slate-900 text-slate-600'}`}
            >
              {step}
            </span>
          ))}
        </div>
      </div>

      <div className="flex-1 bg-black/80 border border-slate-900 rounded-2xl p-4 overflow-y-auto font-mono text-[12px] text-emerald-400 flex flex-col gap-1.5 select-all scrollbar-thin scrollbar-thumb-slate-800">
        {logs.length === 0 ? (
          <div className="flex h-full min-h-40 flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-800 bg-slate-950/40 px-4 text-center font-sans">
            <strong className="text-xs font-black text-slate-400">대기 중</strong>
            <span className="text-[11px] font-semibold leading-relaxed text-slate-600">
              글 생성 또는 자동 발행을 시작하면 단계별 로그가 여기에 표시됩니다.
            </span>
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="leading-relaxed whitespace-pre-wrap">
              <span className="text-slate-600 select-none">&gt;</span> {log}
            </div>
          ))
        )}
        <div ref={terminalEndRef} />
      </div>
    </section>
  );
});

export default TerminalLog;
