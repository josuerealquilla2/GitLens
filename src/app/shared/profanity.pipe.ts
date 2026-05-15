import { Pipe, PipeTransform } from '@angular/core';

const PALABROTAS = [
  'puta','puto','putos','putas','coño','coños','joder','hostia','hostias',
  'mierda','mierdas','cabron','cabrón','cabrones','gilipollas','idiota',
  'imbecil','imbécil','imbeciles','pendejo','pendeja','pendejada','verga',
  'chinga','chingada','chingado','fuck','shit','bitch','asshole','bastard',
  'cunt','dick','pussy','motherfucker','ass','bollocks','wanker','twat',
  'follar','folla','follas','pollas','polla','capullo','capullos','maricón',
  'marica','culo','culos','zorra','zorras','perra','perras','subnormal',
  'retrasado','retrasada','mongolo','mongola'
];

@Pipe({ name: 'profanity', standalone: true, pure: true })
export class ProfanityPipe implements PipeTransform {
  transform(value: string): string {
    if (!value) return value;
    let result = value;
    for (const word of PALABROTAS) {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      result = result.replace(regex, '*'.repeat(word.length));
    }
    return result;
  }
}
