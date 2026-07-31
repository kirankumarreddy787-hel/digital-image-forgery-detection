import streamlit as st
#import option_menu from streamlit
from PIL import Image
import hashlib
import cv2
import numpy as np
from skimage.feature import local_binary_pattern
from skimage.feature import graycomatrix, graycoprops

import matplotlib.pyplot as plt
from PIL import Image
from api import process_image
GROQ_API_KEY = "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"
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(
    temperature=0.5,
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)
# ---------------------------
# Helper Functions
# ---------------------------

# Generate SHA-256 hash
def generate_hash(image):
    img_bytes = image.tobytes()
    return hashlib.sha256(img_bytes).hexdigest()

# Convert PIL to OpenCV
def pil_to_cv(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# Step 3: Pre-processing
def preprocess_image(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.GaussianBlur(gray, (5,5), 0)
    return gray, denoised

# Step 4: Texture Features
def extract_texture_features(gray_img):
    # LBP
    lbp = local_binary_pattern(gray_img, P=8, R=1, method='uniform')
    
    # GLCM
    glcm = graycomatrix(gray_img, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast')[0,0]
    dissimilarity = graycoprops(glcm, 'dissimilarity')[0,0]
    homogeneity = graycoprops(glcm, 'homogeneity')[0,0]
    energy = graycoprops(glcm, 'energy')[0,0]
    correlation = graycoprops(glcm, 'correlation')[0,0]

    glcm_features = {
        "Contrast": contrast,
        "Dissimilarity": dissimilarity,
        "Homogeneity": homogeneity,
        "Energy": energy,
        "Correlation": correlation
    }

    return lbp, glcm_features

# Step 5: Colour Features
def extract_color_features(cv_img):
    channels = {}
    histograms = {}

    # RGB
    for i, col in enumerate(['R','G','B']):
        hist = cv2.calcHist([cv_img], [i], None, [256], [0,256])
        histograms[col] = hist
        channels[col] = cv_img[:,:,i]

    # HSV
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    for i, col in enumerate(['H','S','V']):
        hist = cv2.calcHist([hsv], [i], None, [256], [0,256])
        histograms[col] = hist
        channels[col] = hsv[:,:,i]

    # YCbCr
    ycbcr = cv2.cvtColor(cv_img, cv2.COLOR_BGR2YCrCb)
    for i, col in enumerate(['Y','Cb','Cr']):
        hist = cv2.calcHist([ycbcr], [i], None, [256], [0,256])
        histograms[col] = hist
        channels[col] = ycbcr[:,:,i]

    return channels, histograms

# Step 6: Feature Fusion (summary)
def feature_fusion(glcm_features, histograms):
    fused_summary = {**glcm_features, **{k: int(np.sum(v)) for k,v in histograms.items()}}
    return fused_summary

dataset = "DFDC"
threshold = 0.5
MODELS = [
    "EfficientNetB4",
    "EfficientNetB4ST",
    "EfficientNetAutoAttB4",
    "EfficientNetAutoAttB4ST"
]

# ==============================
# Utility: Safe Result Handling
# ==============================
def safe_result(result, prob):
    if result is None:
        return "unknown", 0.0
    if prob is None:
        return result.lower(), 0.0
    return result.lower(), float(prob)
import cv2
import numpy as np
from PIL import Image

def highlight_forged_regions(pil_image):
    """
    Performs edge detection to highlight possible forged regions.
    Returns a heatmap overlaid on the original image.
    """
    # Convert PIL image to OpenCV format
    img_cv = np.array(pil_image)

    # Handle grayscale or RGBA images
    if len(img_cv.shape) == 2:  # grayscale
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)
    elif img_cv.shape[2] == 4:  # RGBA
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2RGB)

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

    # Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Canny Edge Detection
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    # Create heatmap from edges
    heatmap = cv2.applyColorMap(edges, cv2.COLORMAP_JET)

    # Overlay heatmap on original image
    overlay = cv2.addWeighted(img_cv, 0.7, heatmap, 0.3, 0)

    return overlay
import tensorflow as tf
def generate_gradcam_heatmap(model, image, last_conv_layer_name="conv2d_1"):
    grad_model = tf.keras.models.Model(
        inputs=model.input,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image)
        predicted_class = tf.argmax(predictions[0])
        loss = predictions[:, predicted_class]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]

    heatmap = tf.reduce_mean(conv_outputs * pooled_grads, axis=-1)
    heatmap = np.maximum(heatmap, 0) / np.max(heatmap)
    return heatmap
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()

def user_home_page():
    # Navigation menu for user dashboard
    st.markdown(
        """
        <style>
        /* Apply background image to the main content area */
        .main {
            background-image: url("https://png.pngtree.com/thumb_back/fh260/background/20240919/pngtree-a-background-of-orange-blue-and-yellow-gradients-with-gritty-appearance-image_16233934.jpg");  
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
    col1,col2=st.columns([6,1])
    col1.markdown( """<h2 style="text-align: center;">Digital Image Forgery Detection using Combined Texture & Colour Analysis..</h2> """, unsafe_allow_html=True )
    with col2:
        if st.button("Logout", type="primary"):
            st.session_state["logged_in"] = False
            st.session_state["current_user"] = None
            navigate_to_page("home")

    col1,col2,col3 = st.columns([1,6,1])
    uploaded_file = col2.file_uploader("Upload an Image", type=["jpg","jpeg","png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)    
        # Step 2: Digital Signature
        image_hash = generate_hash(image)
        print(f"Generated Image Hash: {image_hash}")
        col1,col2,col3 = st.columns([1,6,1])
        user_hash = col2.text_input("Enter Signature / Hash to Verify Image")
        col1,col2,col3 = st.columns([1.3,1,1])
        if col2.button("Verify Image",type="primary"):
            if user_hash == image_hash:
                col1,col2,col3 = st.columns([1,6,1])
                col2.success("✅ Congratulations! The image is authentic and Verified Successfully...")
                import numpy as np
                # ---------------------------
                # Step 3: Pre-processing
                # ---------------------------
                cv_img = pil_to_cv(image)
                gray, denoised = preprocess_image(cv_img)

                lbp, glcm_features = extract_texture_features(gray)

                st.subheader("LBP Texture Map")
                # Normalize LBP to 0-255 and convert to uint8
                lbp_normalized = ((lbp - lbp.min()) / (lbp.max() - lbp.min()) * 255).astype(np.uint8)
                            #display pre-processing results in 2 columns
                with st.container(border=True):
                    col1, col2 = st.columns([1,1])
                    col1.image(image, caption="Original Image", use_column_width=True)
                    col2.image(gray, caption="Grayscale Image", channels="GRAY", use_column_width=True)
                    
                with st.container(border=True):
                    col1, col2 = st.columns([1,1])
                    col1.image(denoised, caption="Denoised Image", channels="GRAY", use_column_width=True)
                    col2.image(lbp_normalized, caption="LBP Texture Map", channels="GRAY", use_column_width=True)

                st.subheader("GLCM Feature Values")
                st.table(glcm_features)

                # ---------------------------
                # Step 5: Colour Feature Extraction
                # ---------------------------
                channels, histograms = extract_color_features(cv_img)
                from matplotlib import pyplot as plt
                st.subheader("RGB Channel Histograms")
                fig, ax = plt.subplots()
                for col in ['R','G','B']:
                    ax.plot(histograms[col], label=col)
                ax.set_title("RGB Histograms")
                ax.legend()
                st.pyplot(fig)

                fused_summary = feature_fusion(glcm_features, histograms)
                st.subheader("Combined Feature Vector Summary")
                st.table(fused_summary)

                # ---------------------------
                # Step 7: Model Prediction
                fake_probs, real_probs = [], []

                for model in MODELS:
                    res, prob = process_image(
                        image=uploaded_file,
                        model=model,
                        dataset=dataset,
                        threshold=threshold
                    )
                    res, prob = safe_result(res, prob)
                    if res == "fake":
                        fake_probs.append(prob)
                    elif res == "real":
                        real_probs.append(prob)

                # Final decision based on majority/confidence
                fake_count, real_count = len(fake_probs), len(real_probs)
                if fake_count > real_count:
                    final_result, confidence = "Forgery", sum(fake_probs)
                elif real_count > fake_count:
                    final_result, confidence = "Authentic", sum(real_probs)
                else:
                    # tie-breaker by confidence sum
                    final_result, confidence = (
                        ("Forgery", sum(fake_probs)) if sum(fake_probs) >= sum(real_probs)
                        else ("Authentic", sum(real_probs))
                    )

                if confidence > 1:
                    confidence = 1.0

                if confidence ==0:
                    confidence = 0.5

                # Display result
                box_color = "#ff4b4b" if final_result == "Forgery" else "#6eb52f"
                bg_color = "#ffecec" if final_result == "Forgery" else "#eef7ea"
                st.markdown(
                    f"""
                    <div style="
                        border-left: 8px solid {box_color};
                        background-color: {bg_color};
                        padding: 15px 20px;
                        border-radius: 10px;
                        margin-top: 10px;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                    ">
                        <h3 style="color:{box_color}; margin-bottom:5px;">
                            Final Prediction: {final_result.upper()}
                        </h3>
                        <p style="color:#555; font-size:14px; margin:0;">
                            Confidence: <b>{confidence:.2f}</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                import cv2
                import numpy as np
                import matplotlib.pyplot as plt

                forged_overlay = highlight_forged_regions(image)  # pass PIL image
                forged_overlay_pil = Image.fromarray(forged_overlay)

                with st.container(border=True):
                    col1, col2 = st.columns([1,1])
                    col1.image(image, caption="Original Image", use_column_width=True)
                    col2.image(forged_overlay_pil, caption="Highlighted Forged Regions", use_column_width=True)

                import os
                model = tf.keras.models.load_model('fusion_model.h5')
                upload_dir = "static/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, uploaded_file.name)

                # Save uploaded file
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                image = cv2.imread(filepath)
                image_resized = cv2.resize(image, (224, 224)) / 255.0
                image_expanded = np.expand_dims(image_resized, axis=0)
                heatmap = generate_gradcam_heatmap(model, image_expanded)
                heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
                heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)

                superimposed = cv2.addWeighted(image, 0.6, heatmap_colored, 0.4, 0)

                heatmap_path = filepath.replace('.', '_heatmap.')
                superimposed_path = filepath.replace('.', '_superimposed.')

                #dispaly gradcam heatmap

                with st.container(border=True):
                    col1, col2 = st.columns([1,1])
                    col1.image(heatmap_colored, caption="Grad-CAM Heatmap", use_column_width=True)
                    col2.image(superimposed, caption="Grad-CAM Superimposed", use_column_width=True)

                #AI analysis summary
                content = f"""
                    Image Authenticity: {final_result.upper()}
                    Confidence Score: {confidence:.2f}

                    Texture Features (GLCM):
                    {glcm_features}

                    Colour Features (Histogram Sums):
                    { {k:int(np.sum(v)) for k,v in histograms.items()} }

                    Highlighted Forged Regions: Displayed in edge heatmap and Grad-CAM overlays.

                    Note: LBP texture map, denoised grayscale image, and other intermediate processing steps were applied.
                """
                def generate_summary(content):
                    prompt_template = """
                    You are an AI forensic analyst.

                    Analyze the following image analysis data and generate a clear, concise forensic summary.
                    Do not give any introduction. Use professional tone.

                    Don't give any markdown formatting. Just plain text summary. 
                    Dont give any conclusion. Just summarize the data in a clear and concise manner.
                    Don't give any recommendations. Just summarize the data in a clear and concise manner.
                    Dont give any Introduction. Just summarize the data in a clear and concise manner.

                    Image Analysis Data:
                    {content}
                    """
                    chain = ChatPromptTemplate.from_template(prompt_template) | llm | StrOutputParser()
                    return chain.invoke({"content": content})
                
                summary_text = generate_summary(content)
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f0f0f0;
                        padding: 15px 20px;
                        border-radius: 10px;
                        margin-top: 20px;
                        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                    ">
                        <h3 style="color:#333; margin-bottom:10px;">
                            Forensic Analysis Summary
                        </h3>
                        <p style="color:#555; font-size:14px; white-space:pre-wrap;">
                            {summary_text}
                        </p>
                        <p style="color:#555; font-size:14px; margin-top:10px;">
                            🔍 Note: This summary is generated by an AI model based on the extracted features and model predictions
                                .
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.error("❌ Tampered Image Detected")
        