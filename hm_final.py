import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# No longer using mplcursors as it's experimental and Plotly is better for hover.

# --- Global Page Configuration ---
st.set_page_config(
    page_title="Heatmap",
    page_icon="🔥",
    layout="wide"
)

# --- Cached Data Loader ---
@st.cache_data
def load_data(uploaded_file):
    """
    Reads an uploaded CSV file into a pandas DataFrame.
    Caches the result to prevent re-reading on rerun.
    """
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error reading the CSV file: {e}")
        return None

# --- Function to generate and display Seaborn Heatmap ---
def display_single_heatmap(data_to_plot, title_suffix=""):
    st.write(f"📊 Heatmap {title_suffix}")

    # --- Heatmap Customization Options (in sidebar for clarity) ---
    with st.sidebar:
        st.subheader("Heatmap Customization")

        # Colormap selection
        cmap_options = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis',
            'Blues', 'Greens', 'Oranges', 'Reds', 'Purples',
            'coolwarm', 'RdBu', 'PiYG', 'Spectral', 'YlGnBu', 'YlOrRd'
        ]
        # Dynamically set default cmap based on data range (if it's correlation-like)
        # Assuming correlation data is typically between -1 and 1
        default_cmap_idx = cmap_options.index('coolwarm') if data_to_plot.min().min() >= -1.0 and data_to_plot.max().max() <= 1.0 else cmap_options.index('viridis')
        selected_cmap = st.selectbox("Select Colormap:", cmap_options, index=default_cmap_idx)

        # Annotations
        show_annotations = st.checkbox("Show Annotations (values in cells)", value=True)
        annot_fmt_default = ".2f" if data_to_plot.min().min() >= -1.0 and data_to_plot.max().max() <= 1.0 else ".1f"
        if show_annotations:
            annot_format = st.text_input("Annotation Format (e.g., .1f, .2f):", value=annot_fmt_default)
        else:
            annot_format = None

        # Lines between cells
        linewidth = st.slider("Line Width between cells:", 0.0, 2.0, 0.5, step=0.1)
        linecolor = st.color_picker("Line Color:", "#262626")

        # Vmin/Vmax for color scale
        st.markdown("---")
        st.write("Color Scale Range (Vmin/Vmax):")
        auto_vmin_vmax = st.checkbox("Auto Vmin/Vmax", value=True)
        vmin_val = None
        vmax_val = None
        if not auto_vmin_vmax:
            col_vmin, col_vmax = st.columns(2)
            vmin_val = col_vmin.number_input("Vmin:", value=float(data_to_plot.min().min()), format="%.2f")
            vmax_val = col_vmax.number_input("Vmax:", value=float(data_to_plot.max().max()), format="%.2f")

        # Center for divergent colormaps (e.g., correlations)
        center_cmap = None
        if selected_cmap in ['coolwarm', 'RdBu', 'PiYG', 'Spectral']: # Common diverging maps
             if st.checkbox("Center Colormap at 0 (for divergent data)", value=True if data_to_plot.min().min() >= -1.0 and data_to_plot.max().max() <= 1.0 else False):
                center_cmap = 0


    # Create the heatmap
    fig, ax = plt.subplots(figsize=(12, 3)) # Increased figure size for better visibility
    sns.heatmap(
        data_to_plot,
        cmap=selected_cmap,
        annot=show_annotations,
        fmt=annot_format,
        linewidths=linewidth,
        linecolor=linecolor,
        vmin=vmin_val,
        vmax=vmax_val,
        center=center_cmap,
        ax=ax # Pass the matplotlib axes to seaborn
    )
    ax.set_title("Generated Heatmap", fontsize=18)
    ax.xaxis.tick_top()
    plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better readability
    plt.yticks(rotation=0) # Keep y-axis labels horizontal
    plt.tight_layout() # Adjust layout to prevent labels from overlapping

    st.pyplot(fig,use_container_width=True) # Display the matplotlib figure in Streamlit

def draw_multi_heatmap(ax, data_to_plot, title_suffix="", key_prefix=""):
    # Heatmap Customization Options (in sidebar for clarity)
    # These controls will now apply to ALL heatmaps, which is likely desired
    # If you want individual controls for each heatmap, you'd need to re-think UI layout
    # For simplicity, I'm keeping them in the sidebar and assuming they apply globally
    # If you need individual controls, you would move these into the for loop in run_app
    # and create columns for them as well.
    with st.sidebar:
        st.markdown(f"---")
        st.subheader(f"Customization for: {key_prefix.replace('heatmap_', '')}")

        cmap_options = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis',
            'Blues', 'Greens', 'Oranges', 'Reds', 'Purples',
            'coolwarm', 'RdBu', 'PiYG', 'Spectral', 'YlGnBu', 'YlOrRd'
        ]
        default_cmap_idx = cmap_options.index('coolwarm') if data_to_plot.min().min() >= -1.0 and data_to_plot.max().max() <= 1.0 else cmap_options.index('viridis')
        selected_cmap = st.selectbox("Select Colormap:", cmap_options, index=default_cmap_idx, key=f"{key_prefix}_cmap_select")

        show_annotations = st.checkbox("Show Annotations (values in cells)", value=True, key=f"{key_prefix}_show_annot")
        annot_fmt_default = ".2f" if data_to_plot.min().min() >= -1.0 and data_to_plot.max().max() <= 1.0 else ".1f"
        if show_annotations:
            annot_format = st.text_input("Annotation Format (e.g., .1f, .2f):", value=annot_fmt_default, key=f"{key_prefix}_annot_fmt")
        else:
            annot_format = None

        linewidth = st.slider("Line Width between cells:", 0.0, 2.0, 0.5, step=0.1, key=f"{key_prefix}_linewidth")
        linecolor = st.color_picker("Line Color:", "#F5E3E3", key=f"{key_prefix}_linecolor")

        st.write("Color Scale Range (Vmin/Vmax):")
        auto_vmin_vmax = st.checkbox("Auto Vmin/Vmax", value=True, key=f"{key_prefix}_auto_vmin_vmax")
        vmin_val = None
        vmax_val = None
        if not auto_vmin_vmax:
            col_vmin, col_vmax = st.columns(2) # These are Streamlit columns, not Matplotlib subplots
            vmin_val = col_vmin.number_input("Vmin:", value=float(data_to_plot.min().min()), format="%.2f", key=f"{key_prefix}_vmin_input")
            vmax_val = col_vmax.number_input("Vmax:", value=float(data_to_plot.max().max()), format="%.2f", key=f"{key_prefix}_vmax_input")

        center_cmap = None
        if selected_cmap in ['coolwarm', 'RdBu', 'PiYG', 'Spectral']:
            if st.checkbox("Center Colormap at 0 (for divergent data)", value=True if data_to_plot.min().min() >= -1.0 and data_to_plot.max().max() <= 1.0 else False, key=f"{key_prefix}_center_cmap"):
                center_cmap = 0

    # Create the heatmap on the provided axis
    sns.heatmap(
        data_to_plot,
        cmap=selected_cmap,
        annot=show_annotations,
        fmt=annot_format,
        linewidths=linewidth,
        linecolor=linecolor,
        vmin=vmin_val,
        vmax=vmax_val,
        center=center_cmap,
        ax=ax
    )
    ax.set_title(f"Heatmap of {title_suffix}", fontsize=12) # Reduced font size for multiple plots
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=45, ha='center') # Use setp for cleaner rotation
    plt.setp(ax.get_yticklabels(), rotation=0)

# --- Main Application Logic ---
def run_app():
    st.title("🔥 Heatmap Data Visualizer")
    st.write("Upload a CSV file and select columns to generate a calendar-style heatmap (Year vs. Month).")
    st.write(f'This app is built with Streamlit version: {st.__version__}')

    # --- File Uploader and Sidebar Controls ---
    with st.sidebar:
        st.header("⚙️ Controls")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    # Main Logic when file is uploaded
    if uploaded_file:
        df = load_data(uploaded_file)

        if df is not None:
            df_copy = df.copy() # Work with a copy to avoid modifying cached df

            st.subheader("📊 Data Preview")
            st.dataframe(df_copy)

            with st.sidebar:
                st.divider()
                all_columns = df_copy.columns.tolist()

                value_column = st.multiselect(
                    "Select the Numeric Value Column:",
                    all_columns[1:],
                    max_selections=3,
                    default=all_columns[1:2] # Default to the first two numeric columns                    # Default to the first numeric column
                )

                agg_function = st.selectbox(
                    "Select Aggregation Method:",
                    ['Sum', 'Mean', 'Median', 'Count', 'Max', 'Min'], # Added Max/Min
                    index=1 # Default to Mean
                )

                # Slider for number of years to display
                st.subheader("Data Display Options")
                num_years_to_display = st.slider(
                    "Limit Years to Display (from most recent):",
                    2, 8, 4 # Min 1, Max 20, Default 5
                )


            # --- Data Processing for Heatmap ---
            try:
                # 1. Convert the selected date column to datetime objects
                df_copy['DATE'] = pd.to_datetime(df_copy['DATE'],format='%d-%m-%y', errors='coerce')

                # 2. Drop rows where date conversion failed or value column is NaN
                df_copy.dropna(subset=['DATE'], inplace=True)
                
                if df_copy.empty:
                    st.error("After processing, no valid data remains. Check your date and value columns or data quality.")
                    return

                # 3. Create year and month_name_short columns
                df_copy['year'] = df_copy['DATE'].dt.year.astype('Int64')
                df_copy['month_name_short'] = df_copy['DATE'].dt.strftime('%m-%b')

                # 4. Create a pivot table for the heatmap
                agg_map = {
                    'Sum': 'sum',
                    'Mean': 'mean',
                    'Median': 'median',
                    'Count': 'count',
                    'Max': 'max',
                    'Min': 'min'
                }

                num_heatmaps = len(value_column)

                # Adjust figsize based on the number of plots to ensure readability
                # Increase overall height slightly to prevent labels from squashing in some cases
                fig, axes = plt.subplots(1, num_heatmaps, figsize=(7.5 * num_heatmaps, 3.5), squeeze=False)
                
                for i, col_name in enumerate(value_column):
                    df_copy[col_name] = pd.to_numeric(df_copy[col_name], errors='coerce')
                    heatmap_data = pd.pivot_table(
                        df_copy,
                        values=col_name,
                        index='year',
                        columns='month_name_short',
                        aggfunc=agg_map[agg_function]
                    )
                    # Sort index chronologically (years - descending) and limit by slider
                    heatmap_data = heatmap_data.sort_index(ascending=False).head(num_years_to_display)
                    #st.write("Processed Data for Heatmap:")
                    #st.dataframe(heatmap_data) # Display the processed data for user review
                    # Display the heatmap using the dedicated function
                    draw_multi_heatmap(axes[0, i],
                        heatmap_data,
                        title_suffix=f"of {agg_function} of '{col_name}'",
                        key_prefix=f"heatmap_{col_name}"
                    )
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)

            except KeyError as ke:
                st.error(f"Column selection error: {ke}. Please ensure the selected columns exist.")
            except Exception as e:
                st.error(f"An error occurred during data processing: {e}")
                st.info("Please ensure you have selected the correct date and numeric value columns, and that your date format is consistent.")

    else:
        st.info("Awaiting a CSV file to be uploaded. Please upload a CSV to get started!")

# Run the main application function
if __name__ == "__main__":
    run_app()


