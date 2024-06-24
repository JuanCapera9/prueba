const container = document.querySelector(".container");
const btnSignIn = document.getElementById("btn-sign-in");
const btnSignUp = document.getElementById("btn-sign-up");

btnSignIn.addEventListener("click",()=>{
   container.classList.remove("toggle");
});
btnSignUp.addEventListener("click",()=>{
   container.classList.add("toggle");
});

document.addEventListener('DOMContentLoaded', (event) => {
   const modal = document.getElementById("flashModal");
   const resetPasswordModal = document.getElementById("resetPasswordModal");
   const span = document.getElementsByClassName("close");

   for (let i = 0; i < span.length; i++) {
       span[i].onclick = function() {
           modal.style.display = "none";
           resetPasswordModal.style.display = "none";
       }
   }

   window.onclick = function(event) {
       if (event.target == modal) {
           modal.style.display = "none";
       } else if (event.target == resetPasswordModal) {
           resetPasswordModal.style.display = "none";
       }
   }

   document.getElementById("forgotPasswordLink").onclick = function() {
       resetPasswordModal.style.display = "block";
   }
});
document.addEventListener('DOMContentLoaded', (event) => {
   const flashModal = document.getElementById("flashModal");
   const resetPasswordModal = document.getElementById("resetPasswordModal");
   const newPasswordModal = document.getElementById("newPasswordModal");
   const spans = document.getElementsByClassName("close");

   for (let i = 0; i < spans.length; i++) {
       spans[i].onclick = function() {
           flashModal.style.display = "none";
           resetPasswordModal.style.display = "none";
           newPasswordModal.style.display = "none";
       }
   }

   window.onclick = function(event) {
       if (event.target == flashModal) {
           flashModal.style.display = "none";
       } else if (event.target == resetPasswordModal) {
           resetPasswordModal.style.display = "none";
       } else if (event.target == newPasswordModal) {
           newPasswordModal.style.display = "none";
       }
   }

   document.getElementById("forgotPasswordLink").onclick = function() {
       resetPasswordModal.style.display = "block";
   }

   // Añade lógica para mostrar el modal de nueva contraseña
   // Este es solo un ejemplo de cómo podrías mostrar el modal
   // Supón que quieres mostrar el modal después de que el usuario haya solicitado el restablecimiento
   // Debes modificar esto según la lógica de tu aplicación
   const showNewPasswordModal = false; // Cambia esto según sea necesario
   if (showNewPasswordModal) {
       newPasswordModal.style.display = "block";
   }
});