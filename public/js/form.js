document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("providerForm");
  const alertBox = document.getElementById("alertBox");
  const submitBtn = document.getElementById("submitBtn");

  // VCC Toggle
  const vccCheckbox = document.getElementById("vcc_active");
  const vccGroup = document.getElementById("vcc_details_group");

  if (vccCheckbox && vccGroup) {
    vccCheckbox.addEventListener("change", function () {
      if (this.checked) {
        vccGroup.classList.add("visible");
      } else {
        vccGroup.classList.remove("visible");
      }
    });
  }

  // Copy Mailing to Physical
  const btnCopyMailing = document.getElementById("btn_copy_mailing");
  if (btnCopyMailing) {
    btnCopyMailing.addEventListener("click", function () {
      document.getElementById("physical_name").value = document.getElementById("mailing_name").value;
      document.getElementById("physical_address").value = document.getElementById("mailing_address").value;
      document.getElementById("physical_city").value = document.getElementById("mailing_city").value;
      document.getElementById("physical_country").value = document.getElementById("mailing_country").value;
      document.getElementById("physical_razon_social").value = document.getElementById("mailing_razon_social").value;
      document.getElementById("physical_cedula_juridica").value = document.getElementById("mailing_cedula_juridica").value;
      document.getElementById("physical_post_code").value = document.getElementById("mailing_post_code").value;
    });
  }

  // Copy Physical to Mailing
  const btnCopyPhysical = document.getElementById("btn_copy_physical");
  if (btnCopyPhysical) {
    btnCopyPhysical.addEventListener("click", function () {
      document.getElementById("mailing_name").value = document.getElementById("physical_name").value;
      document.getElementById("mailing_address").value = document.getElementById("physical_address").value;
      document.getElementById("mailing_city").value = document.getElementById("physical_city").value;
      document.getElementById("mailing_country").value = document.getElementById("physical_country").value;
      document.getElementById("mailing_razon_social").value = document.getElementById("physical_razon_social").value;
      document.getElementById("mailing_cedula_juridica").value = document.getElementById("physical_cedula_juridica").value;
      document.getElementById("mailing_post_code").value = document.getElementById("physical_post_code").value;
    });
  }

  // Form Submission
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      alertBox.className = "alert-box";
      alertBox.style.display = "none";

      submitBtn.disabled = true;
      const originalText = submitBtn.innerText;
      submitBtn.innerText = form.getAttribute("data-loading-text") || "Submitting...";

      const formData = new FormData(form);
      const payload = {};
      formData.forEach((value, key) => {
        payload[key] = value;
      });

      // Checkbox conversion
      payload["vcc_active"] = vccCheckbox ? vccCheckbox.checked : false;

      try {
        const response = await fetch("/api/submit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok && result.success) {
          alertBox.className = "alert-box success";
          alertBox.innerHTML = `<strong>✔ ${result.message}</strong> (Reference ID: #${result.id})`;
          alertBox.style.display = "block";
          form.reset();
          if (vccGroup) vccGroup.classList.remove("visible");
          window.scrollTo({ top: 0, behavior: "smooth" });
        } else {
          alertBox.className = "alert-box error";
          alertBox.innerHTML = `<strong>✖ Error:</strong> ${result.error || "Submission failed. Please check the required fields."}`;
          alertBox.style.display = "block";
          alertBox.scrollIntoView({ behavior: "smooth" });
        }
      } catch (err) {
        alertBox.className = "alert-box error";
        alertBox.innerHTML = `<strong>✖ Network Error:</strong> Unable to connect to the server. Please try again.`;
        alertBox.style.display = "block";
        alertBox.scrollIntoView({ behavior: "smooth" });
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = originalText;
      }
    });
  }
});
