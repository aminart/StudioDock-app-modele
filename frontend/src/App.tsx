import React from "react";

/*
 * Modèle d'écran d'une app de la suite. À garder : l'en-tête commun (nn-appbar) et ses trois zones dans cet ordre,
 * le titre de page (nn-page-head), les jetons de couleur. À remplacer : le contenu des pages.
 * Règle : seule l'icône de l'app a sa couleur propre ; tout le reste suit Night Navy.
 * nn-card ne fixe pas de marge intérieure : ajoutez-la (p-5, p-6) selon le contenu.
 */

type Page = "accueil" | "a-propos";

interface Sante {
  name: string;
  version: string;
}

interface Resultat {
  mots: number;
  caracteres: number;
  majuscules: string;
}

interface EtatIA {
  configure: boolean;
  connexion?: string;
  modele?: string;
  local?: boolean;
}

const PAGES: { id: Page; label: string }[] = [
  { id: "accueil", label: "Accueil" },
  { id: "a-propos", label: "À propos" },
];

const pageDepuisAdresse = (): Page => (window.location.hash === "#/a-propos" ? "a-propos" : "accueil");

export const App: React.FC = () => {
  const [page, setPage] = React.useState<Page>(pageDepuisAdresse);
  const [sante, setSante] = React.useState<Sante | null>(null);

  React.useEffect(() => {
    const suivre = () => setPage(pageDepuisAdresse());
    window.addEventListener("hashchange", suivre);
    fetch("/health").then((r) => r.json()).then(setSante).catch(() => undefined);
    return () => window.removeEventListener("hashchange", suivre);
  }, []);

  const nom = sante?.name ?? "Mon app";
  React.useEffect(() => { document.title = nom; }, [nom]);

  return (
    <div className="min-h-screen bg-bg text-ink-body">
      <header className="nn-appbar sticky top-0 z-10">
        {/* 1 · Identité : icône (sa couleur propre) et nom */}
        <a className="nn-appbar-brand" href="#/">
          <img className="nn-appbar-icon" src="/icone.svg" alt="" />
          {nom}
        </a>
        {/* 2 · Navigation : onglets, l'actif porte aria-current */}
        <nav className="nn-appbar-nav" aria-label="Navigation principale">
          {PAGES.map((p) => (
            <a key={p.id} className="nn-appbar-tab" href={p.id === "accueil" ? "#/" : `#/${p.id}`}
              aria-current={page === p.id ? "page" : undefined}>
              {p.label}
            </a>
          ))}
        </nav>
        {/* 3 · Utilitaires, dans cet ordre : aide, langue, thème, réglages (omettre ceux qui manquent) */}
        <div className="nn-appbar-tools">
          <BoutonTheme />
        </div>
      </header>

      <main className="mx-auto flex max-w-[1080px] flex-col gap-6 px-6 py-8">
        {page === "accueil" ? <Accueil /> : <APropos sante={sante} />}
      </main>
    </div>
  );
};

const BoutonTheme: React.FC = () => {
  const [sombre, setSombre] = React.useState(() => window.NightNavy?.current() === "dark");
  React.useEffect(() => {
    const suivre = () => setSombre(window.NightNavy.current() === "dark");
    document.documentElement.addEventListener("nn-themechange", suivre);
    return () => document.documentElement.removeEventListener("nn-themechange", suivre);
  }, []);
  return (
    <button type="button" className="nn-icon-btn" onClick={() => window.NightNavy.toggle()}
      aria-label={sombre ? "Passer en thème clair" : "Passer en thème sombre"} title="Changer de thème">
      {sombre ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
        </svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
        </svg>
      )}
    </button>
  );
};

/* ---------- Page d'exemple : un outil simple (formulaire → résultat) ---------- */

const Accueil: React.FC = () => {
  const [texte, setTexte] = React.useState("");
  const [resultat, setResultat] = React.useState<Resultat | null>(null);
  const [erreur, setErreur] = React.useState<string | null>(null);
  const [occupe, setOccupe] = React.useState(false);

  const analyser = async (e: React.FormEvent) => {
    e.preventDefault();
    setOccupe(true);
    setErreur(null);
    try {
      const r = await fetch("/api/exemple", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ texte }),
      });
      const donnees = await r.json();
      if (!r.ok) throw new Error(typeof donnees.detail === "string" ? donnees.detail : "Analyse impossible.");
      setResultat(donnees);
    } catch (err) {
      setErreur(err instanceof Error ? err.message : "Analyse impossible.");
    } finally {
      setOccupe(false);
    }
  };

  return (
    <>
      <div className="nn-page-head">
        <div>
          <h1 className="nn-page-title">Analyser un texte</h1>
          <p className="nn-page-subtitle">Un exemple d'outil : remplacez cette page par celle de votre app.</p>
        </div>
      </div>

      <form onSubmit={analyser} className="nn-card flex flex-col gap-4 p-6">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="texte" className="text-sm font-medium text-ink">Texte</label>
          <textarea id="texte" className="nn-input min-h-[120px] py-2.5" value={texte}
            onChange={(e) => setTexte(e.target.value)} aria-describedby="texte-aide" />
          <span id="texte-aide" className="text-[13px] text-ink-muted">Collez un paragraphe, puis lancez l'analyse.</span>
        </div>
        {erreur && (
          <p role="alert" className="m-0 rounded border border-danger bg-danger-soft px-4 py-3 text-sm text-danger-text">{erreur}</p>
        )}
        <div className="flex gap-2">
          <button type="submit" className="nn-btn nn-btn-primary" disabled={occupe || !texte.trim()}>
            {occupe ? "Analyse…" : "Analyser"}
          </button>
          {resultat && (
            <button type="button" className="nn-btn nn-btn-secondary" onClick={() => { setTexte(""); setResultat(null); }}>
              Effacer
            </button>
          )}
        </div>
      </form>

      {resultat ? (
        <section aria-labelledby="resultat-titre" className="flex flex-col gap-3">
          <h2 id="resultat-titre" className="m-0 text-[19px] font-bold text-ink">Résultat</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Chiffre label="Mots" valeur={resultat.mots} />
            <Chiffre label="Caractères" valeur={resultat.caracteres} />
          </div>
          <p className="nn-card m-0 break-words p-5 font-mono text-sm">{resultat.majuscules}</p>
        </section>
      ) : (
        <p className="m-0 rounded-lg border border-dashed border-line-dashed px-6 py-8 text-center text-sm text-ink-muted">
          Le résultat de l'analyse apparaîtra ici.
        </p>
      )}
    </>
  );
};

const Chiffre: React.FC<{ label: string; valeur: number }> = ({ label, valeur }) => (
  <div className="nn-card flex flex-col gap-2 p-5">
    <span className="text-[13px] text-ink-muted">{label}</span>
    <span className="text-[28px] font-bold leading-none text-ink">{valeur.toLocaleString("fr-FR")}</span>
  </div>
);

/* ---------- À propos : version et modèle d'IA réglé dans Studio Dock ---------- */

const APropos: React.FC<{ sante: Sante | null }> = ({ sante }) => {
  const [ia, setIa] = React.useState<EtatIA | null>(null);
  React.useEffect(() => {
    fetch("/api/ia").then((r) => r.json()).then(setIa).catch(() => setIa({ configure: false }));
  }, []);

  return (
    <>
      <div className="nn-page-head">
        <div>
          <h1 className="nn-page-title">À propos</h1>
          <p className="nn-page-subtitle">Version de l'app et modèle d'IA qu'elle reçoit de Studio Dock.</p>
        </div>
      </div>
      <dl className="nn-card m-0 grid gap-x-6 gap-y-3 p-6 text-sm" style={{ gridTemplateColumns: "180px minmax(0, 1fr)" }}>
        <dt className="text-ink-muted">Version</dt>
        <dd className="m-0 text-ink">{sante?.version ?? "…"}</dd>
        <dt className="text-ink-muted">Modèle d'IA</dt>
        <dd className="m-0">
          {!ia ? "…" : ia.configure ? (
            <span className="nn-chip nn-chip-ia">{ia.modele} · {ia.connexion}</span>
          ) : (
            <span className="text-ink-muted">Aucun : à régler dans Studio Dock, Réglages › Modèles d'IA.</span>
          )}
        </dd>
      </dl>
    </>
  );
};
