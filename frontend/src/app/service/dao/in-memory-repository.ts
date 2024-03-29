import {InMemoryDbService} from "angular-in-memory-web-api";

export class InMemoryRepository extends InMemoryDbService {

  createDb() {
    console.log('Inizializzato db');
    let utenti = [
      {id: 1, email: "admin@unibas.it", password: "Admin!"},
      {id: 2, email: "utente@unibas.it", password: "Utente!"},
    ];
    return {utenti};
  }

}
