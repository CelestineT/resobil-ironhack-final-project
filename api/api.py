"""
api.py
-------
API REST RESOBIL.

Compétence RNCP visée : C5 (Développer des API pour mettre à disposition
des données traitées).

Endpoints :
    GET  /api/v1/antennes
    GET  /api/v1/antennes/<id_antenne>
    GET  /api/v1/membres?id_antenne=<id>
    GET  /api/v1/projets
    GET  /api/v1/production-agricole?id_antenne=<id>
    GET  /api/v1/impact-social/<id_antenne>
    GET  /api/v1/health

Lancement local :
    flask --app api run --debug
"""

import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)


def get_db():
    return mysql.connector.connect(
        host=os.environ["AZURE_MYSQL_HOST"],
        port=int(os.environ.get("AZURE_MYSQL_PORT", 3306)),
        user=os.environ["AZURE_MYSQL_USER"],
        password=os.environ["AZURE_MYSQL_PASSWORD"],
        database=os.environ["AZURE_MYSQL_DATABASE"],
        ssl_disabled=False,
    )


def query(sql, params=None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/v1/antennes", methods=["GET"])
def get_antennes():
    rows = query(
        "SELECT id_antenne, nom, localisation, nb_membres, nb_membres_actifs, "
        "activite_principale, statut FROM antenne"
    )
    return jsonify(rows), 200


@app.route("/api/v1/antennes/<int:id_antenne>", methods=["GET"])
def get_antenne(id_antenne):
    rows = query("SELECT * FROM antenne WHERE id_antenne = %s", (id_antenne,))
    if not rows:
        return jsonify({"error": "Antenne introuvable"}), 404
    return jsonify(rows[0]), 200


@app.route("/api/v1/membres", methods=["GET"])
def get_membres():
    id_antenne = request.args.get("id_antenne", type=int)
    if id_antenne:
        rows = query(
            "SELECT m.id_membre, m.nom, m.prenom, m.localite, ma.date_debut, ma.actif "
            "FROM membre m JOIN membre_antenne ma ON m.id_membre = ma.id_membre "
            "WHERE ma.id_antenne = %s",
            (id_antenne,),
        )
    else:
        rows = query("SELECT id_membre, nom, prenom, localite FROM membre")
    return jsonify(rows), 200


@app.route("/api/v1/projets", methods=["GET"])
def get_projets():
    rows = query(
        "SELECT id_projet, titre, budget, devise, statut, date_debut, date_fin FROM projet"
    )
    return jsonify(rows), 200


@app.route("/api/v1/production-agricole", methods=["GET"])
def get_production_agricole():
    id_antenne = request.args.get("id_antenne", type=int)
    if id_antenne:
        rows = query(
            "SELECT * FROM production_agricole WHERE id_antenne = %s", (id_antenne,)
        )
    else:
        rows = query("SELECT * FROM production_agricole")
    return jsonify(rows), 200


@app.route("/api/v1/impact-social/<int:id_antenne>", methods=["GET"])
def get_impact_social(id_antenne):
    rows = query("SELECT * FROM impact_social WHERE id_antenne = %s", (id_antenne,))
    return jsonify(rows), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ressource non trouvée"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erreur interne du serveur"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
