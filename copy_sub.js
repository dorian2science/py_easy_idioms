function copysub2(){
  let captions = document.querySelectorAll('.captions-text .ytp-caption-segment');
  let fullText = Array.from(captions).map(el => el.innerText).join(' ');

  // Création d'un champ temporaire
  let textarea = document.createElement('textarea');
  // textarea.value = "explique moi cette phrase mot par mot: " + fullText;
  textarea.value = fullText;
  document.body.appendChild(textarea);

  // Sélection + copie
  textarea.select();
  document.execCommand('copy');

  // Nettoyage
  document.body.removeChild(textarea);
  console.log("✅ Texte copié dans le presse-papiers (via textarea).")
}
