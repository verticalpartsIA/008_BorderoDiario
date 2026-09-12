from __future__ import annotations

import re
from typing import Any

from mcp.server.fastmcp import FastMCP

from .audit import write_audit
from .config import settings
from .evolution import evolution

mcp = FastMCP(
    "VerticalParts WhatsApp",
    host=settings.mcp_host,
    port=settings.mcp_port,
)


def _numero(valor: str) -> str:
    digits = re.sub(r"\D", "", valor or "")
    if len(digits) in {10, 11}:
        digits = "55" + digits
    if len(digits) < 12 or len(digits) > 13:
        raise ValueError("Número inválido. Informe DDI+DDD+número.")
    return digits


def _remote_jid(valor: str) -> str:
    value = (valor or "").strip()
    if value.endswith("@s.whatsapp.net") or value.endswith("@lid") or value.endswith("@c.us"):
        return value
    return f"{_numero(value)}@s.whatsapp.net"


@mcp.tool()
async def whatsapp_status() -> Any:
    """Consulta o estado da instância corporativa de WhatsApp na Evolution API."""
    result = await evolution.status()
    write_audit("whatsapp_status", {"ok": True})
    return result


@mcp.tool()
async def whatsapp_verificar_numero(numero: str) -> Any:
    """Verifica se um telefone pode ser localizado no WhatsApp. Aceita número brasileiro com ou sem DDI 55."""
    normalized = _numero(numero)
    result = await evolution.verificar_numero(normalized)
    write_audit("whatsapp_verificar_numero", {"numero": normalized, "ok": True})
    return result


@mcp.tool()
async def whatsapp_enviar_texto(numero: str, mensagem: str) -> Any:
    """Envia uma mensagem de texto pelo WhatsApp corporativo. Escritas ficam bloqueadas enquanto WHATSAPP_MCP_ALLOW_WRITES=false."""
    if not settings.allow_writes:
        raise PermissionError(
            "Envio bloqueado por segurança. Defina WHATSAPP_MCP_ALLOW_WRITES=true somente após homologação."
        )
    normalized = _numero(numero)
    text = (mensagem or "").strip()
    if not text:
        raise ValueError("A mensagem não pode ser vazia.")
    result = await evolution.enviar_texto(normalized, text)
    message_id = None
    if isinstance(result, dict):
        message_id = (result.get("key") or {}).get("id")
    write_audit(
        "whatsapp_enviar_texto",
        {
            "numero": normalized,
            "message_id": message_id,
            "chars": len(text),
            "ok": True,
        },
    )
    return result


@mcp.tool()
async def whatsapp_buscar_mensagens(contato: str, limite: int = 20) -> Any:
    """Busca o histórico recente de mensagens de um telefone ou remoteJid. Não altera dados."""
    jid = _remote_jid(contato)
    result = await evolution.buscar_mensagens(jid, limite)
    write_audit("whatsapp_buscar_mensagens", {"remote_jid": jid, "limite": limite, "ok": True})
    return result


def main() -> None:
    settings.validate()
    transport = settings.mcp_transport.strip().lower()
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise RuntimeError(f"MCP_TRANSPORT inválido: {transport}")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
