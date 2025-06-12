import pandas as pd
import streamlit as st

def simulate(
    CHARGE_COUT_PAR_MACHINE=15000,
    CHARGE_COUT_DEPLACEMENT_PAR_ABO=500,
    CHARGES_SALAIRE_SOUHAITE=0,
    CHARGES_REMBOURSEMENT_PRET=0,
    CHARGE_DIVERSES=1000,
    CA_PRIX_REVIENT_PAR_COMMANDE=25000,
    CA_PRIX_ABONNEMENT=1000,
    COMMANDES_MENSUELLES=2,
    TEMPS_MONTAGE_MOIS=2,
    TEMPS_AVANT_ABONNEMENT_MOIS=3,
    PRET_INITIAL=50000
):
    df = pd.DataFrame(index=range(1, 25))
    df.index.name = 'MOIS'

    df['COMMANDES'] = COMMANDES_MENSUELLES
    df['MACHINES_LIVREES'] = df['COMMANDES'].shift(TEMPS_MONTAGE_MOIS, fill_value=0).cumsum()
    df['ABONNEMENTS_ACTIFS'] = df['MACHINES_LIVREES'].shift(TEMPS_AVANT_ABONNEMENT_MOIS, fill_value=0)

    df['CA_COMMANDES'] = 0.5 * CA_PRIX_REVIENT_PAR_COMMANDE * df['COMMANDES'] + \
                         0.5 * CA_PRIX_REVIENT_PAR_COMMANDE * df['MACHINES_LIVREES'].diff().fillna(0)
    df['CA_ABONNEMENTS'] = CA_PRIX_ABONNEMENT * df['ABONNEMENTS_ACTIFS']

    df['COUT_MACHINE'] = CHARGE_COUT_PAR_MACHINE * df['COMMANDES']
    df['COUT_DEPLACEMENT'] = CHARGE_COUT_DEPLACEMENT_PAR_ABO * df['ABONNEMENTS_ACTIFS']
    df['COUT_CREDIT_SALAIRES_AUTRES'] = CHARGES_REMBOURSEMENT_PRET + CHARGES_SALAIRE_SOUHAITE + CHARGE_DIVERSES

    df['BENEFICE'] = df['CA_COMMANDES'] + df['CA_ABONNEMENTS'] - (
        df['COUT_MACHINE'] + df['COUT_DEPLACEMENT'] + df['COUT_CREDIT_SALAIRES_AUTRES']
    )
    df['CUMUL_CASH'] = df['BENEFICE'].cumsum() + PRET_INITIAL

    return df.reset_index()

# Interface web Streamlit
st.set_page_config(page_title="APL", layout="wide")

cols = st.columns(6)
with cols[0]:
    CHARGE_COUT_PAR_MACHINE = st.number_input("CHARGE: coût machine (/u)", value=15000)
    CHARGES_SALAIRE_SOUHAITE = st.number_input("CHARGE: salaire souhaité (brut)", value=0)


with cols[1]:
    CHARGE_COUT_DEPLACEMENT_PAR_ABO = st.number_input("CHARGE: coût déplacement / abo", value=500)
    CHARGES_REMBOURSEMENT_PRET = st.number_input("CHARGE: Mensualité remboursement prêt", value=1000)


with cols[2]:
    CHARGE_DIVERSES = st.number_input("CHARGE: diverses (loyer, pub, SEO)", value=1000)
    TEMPS_MONTAGE_MOIS = st.number_input("Temps de montage (mois, après commande)", value=2)


with cols[3]:
    TEMPS_AVANT_ABONNEMENT_MOIS = st.number_input("Mois avant début abo (après commande)", value=3)
    COMMANDES_MENSUELLES = st.number_input("Commandes mensuelles", value=1)

with cols[4]:
    CA_PRIX_ABONNEMENT = st.number_input("CA: Prix abonnement mensuel", value=750)
    CA_PRIX_REVIENT_PAR_COMMANDE = st.number_input("CA: Prix facturé au client (/machine)", value=25000)

with cols[5]:
    PRET_INITIAL = st.number_input("CA: Capital initial (prêt)", value=50000)

params = dict(
    CHARGE_COUT_PAR_MACHINE=CHARGE_COUT_PAR_MACHINE,
    CHARGE_COUT_DEPLACEMENT_PAR_ABO=CHARGE_COUT_DEPLACEMENT_PAR_ABO,
    CHARGES_SALAIRE_SOUHAITE=CHARGES_SALAIRE_SOUHAITE,
    CHARGES_REMBOURSEMENT_PRET=CHARGES_REMBOURSEMENT_PRET,
    CHARGE_DIVERSES=CHARGE_DIVERSES,
    CA_PRIX_REVIENT_PAR_COMMANDE=CA_PRIX_REVIENT_PAR_COMMANDE,
    CA_PRIX_ABONNEMENT=CA_PRIX_ABONNEMENT,
    COMMANDES_MENSUELLES=COMMANDES_MENSUELLES,
    TEMPS_MONTAGE_MOIS=TEMPS_MONTAGE_MOIS,
    TEMPS_AVANT_ABONNEMENT_MOIS=TEMPS_AVANT_ABONNEMENT_MOIS,
    PRET_INITIAL=PRET_INITIAL
)

df = simulate(**params)
st.dataframe(df, use_container_width=True)

st.text("Chaque commande déclenche 50% du paiement à la commande, 50% à la livraison (après 'Temps de montage').")
st.text("Le 'Temps de montage' inclut commande et assemblage des pièces.")
st.text("'Machines livrées' est un cumul des machines prêtes, pas celles du mois.")
st.text("Les abonnements commencent 3 mois après chaque livraison (modifiable via 'Temps avant début abo').")
st.text("Les charges fixes mensuelles incluent salaire, prêt et charges diverses, constantes sur la période.")
st.text("Le produit étant hors-ligne, il faut des déplacements pour la maintenance (qui ne sera sûrement pas mensuelle).")
