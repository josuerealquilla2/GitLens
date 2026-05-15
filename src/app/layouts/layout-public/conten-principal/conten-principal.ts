import { Component } from '@angular/core';
import { ReposSinRegistro } from '../repos-sin-registro/repos-sin-registro';

export interface LangCard {
  label: string;
  icon: string;
  color: string;
}

@Component({
  selector: 'app-conten-principal',
  imports: [ReposSinRegistro],
  templateUrl: './conten-principal.html',
  styleUrl: './conten-principal.scss',
  standalone: true,
})
export class ContenPrincipal {

  // 20 lenguajes repartidos en 4 columnas (5 cada una, duplicados en HTML para loop infinito)
  readonly colL1: LangCard[] = [
    { label: 'JavaScript', icon: 'JS',  color: '#F7DF1E' },
    { label: 'Python',     icon: 'PY',  color: '#3776AB' },
    { label: 'TypeScript', icon: 'TS',  color: '#3178C6' },
    { label: 'Rust',       icon: 'RS',  color: '#DEA584' },
    { label: 'Go',         icon: 'Go',  color: '#00ADD8' },
  ];

  readonly colL2: LangCard[] = [
    { label: 'Kotlin',  icon: 'KT',  color: '#7F52FF' },
    { label: 'Swift',   icon: 'SW',  color: '#F05138' },
    { label: 'Ruby',    icon: 'RB',  color: '#CC342D' },
    { label: 'PHP',     icon: 'PHP', color: '#777BB4' },
    { label: 'C++',     icon: 'C++', color: '#00599C' },
  ];

  readonly colR1: LangCard[] = [
    { label: 'Java',  icon: 'J',   color: '#007396' },
    { label: 'C#',    icon: 'C#',  color: '#178600' },
    { label: 'HTML',  icon: 'HT',  color: '#E34F26' },
    { label: 'CSS',   icon: 'CSS', color: '#264DE4' },
    { label: 'Dart',  icon: 'DT',  color: '#00B4AB' },
  ];

  readonly colR2: LangCard[] = [
    { label: 'Shell',  icon: 'SH',  color: '#89E051' },
    { label: 'Scala',  icon: 'SC',  color: '#DC322F' },
    { label: 'R',      icon: 'R',   color: '#198CE7' },
    { label: 'Lua',    icon: 'LU',  color: '#000080' },
    { label: 'Elixir', icon: 'EX',  color: '#6E4A7E' },
  ];
}
