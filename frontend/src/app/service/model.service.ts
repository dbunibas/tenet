import {Injectable} from '@angular/core';
import {C} from './c';

@Injectable({
  providedIn: 'root'
})
export class ModelService {

  private beans: Map<C, any> = new Map<C, any>();

  constructor() {
  }

  getBean<T>(key: C): T | undefined {
    return this.beans.get(key);
  }

  putBean<T>(key: C, bean: T): void {
    this.beans.set(key, bean);
  }

  removeBean(key: C): void {
    this.beans.delete(key);
  }

  getPersistentBean<T>(key: C): T | undefined {
    let bean = this.beans.get(key);
    if (!bean) {
      let json = localStorage.getItem(C[key]);
      if (json) {
        bean = JSON.parse(json);
        this.putBean(key, bean);
      }
    }
    return bean;
  }

  putPersistentBean<T>(key: C, bean: T) {
    this.beans.set(key, bean);
    localStorage.setItem(C[key], JSON.stringify(bean));
  }

  removePersistentBean(key: C) {
    this.beans.delete(key);
    localStorage.removeItem(C[key]);
  }

  clear() {
    this.beans.clear();
    localStorage.clear();
  }


  showLoadingSpinner(): void {
    this.putBean(C.LOADING, true);
  }

  hideLoadingSpinnner(): void {
    this.removeBean(C.LOADING);
  }
}
