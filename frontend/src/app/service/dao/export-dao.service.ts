import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { lastValueFrom } from 'rxjs';
import { environment } from 'src/environments/environment';
import { BYPASS_LOADING } from '../interceptors/loading.interceptor';
import { Export } from 'src/app/model/export';

@Injectable({
  providedIn: 'root'
})
export class ExportDaoService {

  constructor(private httpClient: HttpClient) { }
  private baseUrl = environment.backendUrl + "/exports";

  getExports(): Promise<Export[]> {
    let url = this.baseUrl;
    return lastValueFrom(this.httpClient.get<Export[]>(url));
  }

  getExport(exportId: string, bypassLoading: boolean = false): Promise<string> {
    let url = `${this.baseUrl}/${exportId}`;
    return lastValueFrom(this.httpClient.get(url, {responseType: "text", context: new HttpContext().set(BYPASS_LOADING, bypassLoading)}));
  }
}
