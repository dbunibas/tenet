import {Injectable} from '@angular/core';
import {environment} from "../../../environments/environment";
import {lastValueFrom} from "rxjs";
import {Evidence} from "../../model/evidence";
import {HttpClient} from "@angular/common/http";
import {Query} from "../../model/query";
import { SemanticQuery } from 'src/app/model/semanticquery';

@Injectable({
  providedIn: 'root'
})
export class EvidenceDAOService {

  constructor(private httpClient: HttpClient) {
  }

  private baseUrl = environment.backendUrl + "/projects";

  getEvidenceList(projectId: string) {
    let url = this.baseUrl + "/" + projectId + "/evidence";
    return lastValueFrom(this.httpClient.get<Evidence[]>(url));
  }

  createEvidence(projectId: string, evidence: Evidence) {
    let url = this.baseUrl + "/" + projectId + "/evidence";
    return lastValueFrom(this.httpClient.post<Evidence>(url, evidence));
  }

  updateEvidence(projectId: string, evidence: Evidence) {
    let url = this.baseUrl + "/" + projectId + "/evidence/" + evidence.id;
    return lastValueFrom(this.httpClient.put(url, evidence));
  }

  getQuery(projectId: string) {
    let url = `${this.baseUrl}/${projectId}/evidence/sql`;
    return lastValueFrom(this.httpClient.get<Query>(url));
  }

  generateEvidences(projectId: string, nPositives: number, nNegatives: number) {
    let url = `${this.baseUrl}/${projectId}/evidence/newEvidence`;
    return lastValueFrom(this.httpClient.post<Evidence[]>(url, {
      "positiveNumber": nPositives,
      "negativeNumber": nNegatives
    }));
  }

  getSemanticQueries(projectId: string, evidence: Evidence): Promise<SemanticQuery[]> {
    let url = `${this.baseUrl}/${projectId}/evidence/${evidence.id!}/semanticQueries`;
    return lastValueFrom(this.httpClient.get<SemanticQuery[]>(url));
  }

  generateSentence(projectId: string, evidence: Evidence, type: SemanticQuery, number: number): Promise<string[]> {
    let url = `${this.baseUrl}/${projectId}/evidence/${evidence.id!}/sentences`;
    return lastValueFrom(this.httpClient.post<string[]>(url, {"sentenceType": type, "number": number}));
  }
}
