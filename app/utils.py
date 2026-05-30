"""Delade hjälpfunktioner."""

import streamlit as st


def is_mobile() -> bool:
    try:
        ua = st.context.headers.get("user-agent", "").lower()
        return any(kw in ua for kw in ("mobile", "android", "iphone", "ipad", "ipod"))
    except Exception:
        return False
