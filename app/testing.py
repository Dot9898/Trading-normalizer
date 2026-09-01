

import pandas as pd
import streamlit as st

df = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie"],
        "view": [":material/visibility: View"] * 3,
    }
)

def handle_view():
    click = st.session_state.view_click
    st.toast(f"Viewing row {click['row']}: {df.iloc[click['row']]['name']}")

st.dataframe(
    df,
    column_config={
        "view": st.column_config.ButtonColumn(
            "", type="tertiary", on_click=handle_view, key="view_click"
        ),
    },
    hide_index=True,
)



