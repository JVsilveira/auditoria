import axios from "axios";

export const uploadPdfs = async (files) => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("pdfs", files[i]);
  }

  const response = await axios.post("http://localhost:8000/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};