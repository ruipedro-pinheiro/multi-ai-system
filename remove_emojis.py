#!/usr/bin/env python3
"""Replace all emoji with professional SVG icons"""

replacements = {
    '🔄': '<i data-lucide="refresh-cw" style="width: 16px; height: 16px;"></i>',
    '💬': '<i data-lucide="message-circle" style="width: 20px; height: 20px;"></i>',
    '👁️': '<i data-lucide="eye" style="width: 16px; height: 16px;"></i>',
    '✅': '<i data-lucide="check-circle" style="width: 16px; height: 16px; color: #10b981;"></i>',
    '❌': '<i data-lucide="x-circle" style="width: 16px; height: 16px; color: #ef4444;"></i>',
    '⚠️': '<i data-lucide="alert-triangle" style="width: 16px; height: 16px; color: #f59e0b;"></i>',
    '🚫': '<i data-lucide="ban" style="width: 16px; height: 16px; color: #ef4444;"></i>',
    '🚀': '<i data-lucide="rocket" style="width: 16px; height: 16px;"></i>',
    '🔍': '<i data-lucide="search" style="width: 16px; height: 16px;"></i>',
    '🤖': '<i data-lucide="bot" style="width: 16px; height: 16px;"></i>',
    '🧠': '<i data-lucide="brain" style="width: 16px; height: 16px;"></i>',
    '🎯': '<i data-lucide="target" style="width: 16px; height: 16px;"></i>',
    '💻': '<i data-lucide="laptop" style="width: 16px; height: 16px;"></i>',
}

with open("/home/chika/app/frontend-v1/index.html", "r") as f:
    content = f.read()

for emoji, icon in replacements.items():
    content = content.replace(emoji, icon)

with open("/home/chika/app/frontend-v1/index.html", "w") as f:
    f.write(content)

print(f"✅ Replaced {len(replacements)} emoji with SVG icons")
