
import requests
import streamlit as st

import os

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)
st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ OpsPilot AI")
st.subheader("Agentic Incident Diagnosis & Resolution Copilot")

st.write(
    "Submit a system log to detect unusual behavior "
    "and retrieve relevant troubleshooting guidance."
)

with st.sidebar:
    st.header("Settings")
    top_k = st.slider(
        "Number of runbooks to retrieve",
        min_value=1,
        max_value=10,
        value=3,
    )

    st.caption("Backend: FastAPI")
    st.caption(API_URL)

log_line = st.text_area(
    "Paste a system log",
    height=150,
    placeholder=(
        "081109 203518 143 INFO "
        "dfs.DataNode$DataXceiver: Receiving block ..."
    ),
)

if st.button("Analyze Log", type="primary"):
    if not log_line.strip():
        st.warning("so Please enter a log line before analyzing.")
    else:
        try:
            with st.spinner("Analyzing log..."):
                response = requests.post(
                    f"{API_URL}/incidents/diagnose",
                    json={
                        "log_line": log_line,
                        "top_k": top_k,
                    },
                    timeout=60,
                )

            if response.status_code != 200:
                try:
                    detail = response.json().get(
                        "detail", response.text
                    )
                except ValueError:
                    detail = response.text

                st.error(
                    f"API error ({response.status_code}): {detail}"
                )
            else:
                result = response.json()
                prediction = result["analysis"]["prediction"]

                st.divider()
                st.header("Diagnosis Results")

                if prediction["is_anomaly"]:
                    st.error("Anomaly flagged by the model")
                else:
                    st.success("No anomaly flagged by the model")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Prediction",
                        prediction["prediction"].upper(),
                    )

                with col2:
                    st.metric(
                        "Anomaly Score",
                        f'{prediction["anomaly_score"]:.5f}',
                    )

                with col3:
                    st.metric(
                        "Runbooks Found",
                        result["troubleshooting"]["results_count"],
                    )

                st.caption(prediction["score_note"])

                st.subheader("Incident Details")
                st.json(result["incident"])

                st.subheader("Extracted Features")
                st.json(result["analysis"]["features"])

                st.subheader("Assessment")
                st.write(result["assessment"])


                # Structured incident assessment
                incident_assessment = result.get("incident_assessment", {})

                st.subheader("Incident Assessment")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Component**")
                    st.write(incident_assessment.get("component", "Unknown"))

                with col2:
                    st.write("**Log level**")
                    st.write(incident_assessment.get("log_level", "Unknown"))

                st.write("**Observed message**")
                st.write(
                    incident_assessment.get(
                        "observed_message",
                        "No message available",
                    )
                )

                st.write("**Root cause**")
                root_cause = incident_assessment.get("root_cause")

                if root_cause:
                    st.write(root_cause)
                else:
                    st.info(
                        "Root cause has not been established. "
                        "Further investigation is required."
                    )

                st.write("**Recommended next steps**")
                recommendations = incident_assessment.get("recommendations", [])

                if recommendations:
                    for recommendation in recommendations:
                        st.markdown(f"- {recommendation}")
                else:
                    st.write("No recommendations available.")

                st.write("**Limitations**")
                limitations = incident_assessment.get("limitations", [])

                for limitation in limitations:
                    st.markdown(f"- {limitation}")


                # LLM-generated explanation
                st.divider()
                st.subheader("AI-Generated Incident Explanation")

                llm_status = result.get("llm_status", "unavailable")
                llm_explanation = result.get("llm_explanation")

                if llm_status == "success" and llm_explanation:
                    st.markdown(llm_explanation)
                else:
                    st.warning(
                        "The AI explanation is currently unavailable. "
                        "You can still use the rule-based assessment and "
                        "troubleshooting results above."
                    )

                st.subheader("Troubleshooting Guidance")
                troubleshooting = result["troubleshooting"]
                runbooks = troubleshooting.get("runbooks", [])

                if runbooks:
                    for index, runbook in enumerate(runbooks, start=1):
                        with st.expander(
                            f"Runbook {index}: "
                            f"{runbook.get('title', 'Untitled')}"
                        ):
                            st.write(
                                "Relevance score:",
                                runbook.get("score", "Not provided"),
                            )
                            st.write(
                                runbook.get(
                                    "content",
                                    runbook.get(
                                        "excerpt",
                                        "No content returned.",
                                    ),
                                )
                            )
                else:
                    st.info(
                        troubleshooting.get(
                            "message",
                            "No matching runbooks were found.",
                        )
                    )

                st.subheader("Limitations")
                for limitation in result.get("limitations", []):
                    st.write(f"- {limitation}")

                st.caption(
                    "An anomaly flag indicates unusual behavior; "
                    "it does not confirm a real incident or its root cause."
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to FastAPI. "
                "Start the backend at http://127.0.0.1:8000 first."
            )
        except requests.exceptions.Timeout:
            st.error("The API request timed out. Please try again.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")
        except (KeyError, TypeError, ValueError) as exc:
            st.error(
                f"The API returned an unexpected response: {exc}"
            )
