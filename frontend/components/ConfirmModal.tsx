"use client";

import { useEffect, useRef } from "react";

interface ConfirmModalProps {
 isOpen: boolean;
 title?: string;
 message: string;
 confirmLabel?: string;
 cancelLabel?: string;
 variant?: "danger" | "warning" | "info";
 onConfirm: () => void;
 onCancel: () => void;
}

export default function ConfirmModal({
 isOpen,
 title = "Confirm Action",
 message,
 confirmLabel = "Confirm",
 cancelLabel = "Cancel",
 variant = "danger",
 onConfirm,
 onCancel,
}: ConfirmModalProps) {
 const confirmBtnRef = useRef<HTMLButtonElement>(null);

 useEffect(() => {
 if (isOpen) confirmBtnRef.current?.focus();
 }, [isOpen]);

 useEffect(() => {
 const handleKey = (e: KeyboardEvent) => {
 if (!isOpen) return;
 if (e.key === "Escape") onCancel();
 if (e.key === "Enter") onConfirm();
 };
 window.addEventListener("keydown", handleKey);
 return () => window.removeEventListener("keydown", handleKey);
 }, [isOpen, onConfirm, onCancel]);

 if (!isOpen) return null;

 const variantStyles = {
 danger: {
 icon: "",
 confirmBg: "var(--confirm-danger-bg, #ef4444)",
 confirmHover: "var(--confirm-danger-hover, #dc2626)",
 iconBg: "rgba(239,68,68,0.12)",
 },
 warning: {
 icon: "",
 confirmBg: "var(--confirm-warning-bg, #f59e0b)",
 confirmHover: "var(--confirm-warning-hover, #d97706)",
 iconBg: "rgba(245,158,11,0.12)",
 },
 info: {
 icon: "",
 confirmBg: "var(--confirm-info-bg, #3b82f6)",
 confirmHover: "var(--confirm-info-hover, #2563eb)",
 iconBg: "rgba(59,130,246,0.12)",
 },
 };

 const v = variantStyles[variant];

 return (
 <>
 <style>{`
 .confirm-overlay {
 position: fixed;
 inset: 0;
 z-index: 9999;
 display: flex;
 align-items: center;
 justify-content: center;
 background: rgba(0, 0, 0, 0.55);
 backdrop-filter: blur(6px);
 animation: confirmFadeIn 0.15s ease;
 }
 @keyframes confirmFadeIn {
 from { opacity: 0; }
 to { opacity: 1; }
 }
 .confirm-card {
 background: #1a1d27;
 border: 1px solid rgba(255,255,255,0.08);
 border-radius: 16px;
 padding: 28px 32px 24px;
 max-width: 420px;
 width: 90%;
 box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04);
 animation: confirmSlideUp 0.18s cubic-bezier(0.34,1.56,0.64,1);
 }
 @keyframes confirmSlideUp {
 from { transform: translateY(16px) scale(0.97); opacity: 0; }
 to { transform: translateY(0) scale(1); opacity: 1; }
 }
 .confirm-icon {
 width: 48px;
 height: 48px;
 border-radius: 12px;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 22px;
 margin-bottom: 16px;
 }
 .confirm-title {
 font-size: 17px;
 font-weight: 600;
 color: #f1f5f9;
 margin: 0 0 8px;
 letter-spacing: -0.2px;
 }
 .confirm-message {
 font-size: 14px;
 color: #94a3b8;
 line-height: 1.6;
 margin: 0 0 24px;
 }
 .confirm-actions {
 display: flex;
 gap: 10px;
 justify-content: flex-end;
 }
 .confirm-btn {
 padding: 9px 20px;
 border-radius: 8px;
 font-size: 14px;
 font-weight: 500;
 cursor: pointer;
 border: none;
 transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
 outline: none;
 }
 .confirm-btn:active { transform: scale(0.97); }
 .confirm-cancel {
 background: rgba(255,255,255,0.06);
 color: #94a3b8;
 border: 1px solid rgba(255,255,255,0.08);
 }
 .confirm-cancel:hover {
 background: rgba(255,255,255,0.1);
 color: #cbd5e1;
 }
 .confirm-ok {
 color: #fff;
 font-weight: 600;
 letter-spacing: 0.2px;
 box-shadow: 0 4px 12px rgba(0,0,0,0.3);
 }
 .confirm-ok:hover { filter: brightness(1.1); }
 .confirm-ok:focus { box-shadow: 0 0 0 3px rgba(255,255,255,0.2); }
 `}</style>

 <div className="confirm-overlay" onClick={onCancel} role="dialog" aria-modal="true" aria-labelledby="confirm-title">
 <div className="confirm-card" onClick={(e) => e.stopPropagation()}>
 <div className="confirm-icon" style={{ background: v.iconBg }}>
 {v.icon}
 </div>
 <h2 className="confirm-title" id="confirm-title">{title}</h2>
 <p className="confirm-message">{message}</p>
 <div className="confirm-actions">
 <button className="confirm-btn confirm-cancel" onClick={onCancel}>
 {cancelLabel}
 </button>
 <button
 ref={confirmBtnRef}
 className="confirm-btn confirm-ok"
 style={{ background: v.confirmBg }}
 onClick={onConfirm}
 >
 {confirmLabel}
 </button>
 </div>
 </div>
 </div>
 </>
 );
}
