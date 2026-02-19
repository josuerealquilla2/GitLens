
import {Injectable} from '@angular/core';
import Swal from 'sweetalert2'

@Injectable({
  providedIn: 'root',
})
export class AlertServices {

  showLoader(title: string = "Cargando...", description: string = "Espere unos segundos") {
    Swal.fire({
      title: title,
      text: description,
      showConfirmButton: false,
      allowOutsideClick: false,
      allowEscapeKey: false,
      didOpen: () => {
        Swal.showLoading()
      }
    })
  }

  confirm(title: string,
          description: string,
          confirmText: string = "¿Esta seguro?",
          cancelText: string = "Cancelar",
          icon: "warning" | "info" | "error" | "success"): void {
  }

  alert(title: string,
        description: string,
        icon: "warning" | "info" | "error" | "success"): void {

    Swal.fire({
      title: title,
      text: description,
      icon: icon,
      showConfirmButton: true,
      allowOutsideClick: true,
      confirmButtonText: "Cerrar notificación"
    })
  }

  popupErrores(err: any) {
    let msg = "Error desconocido. Contacte con soporte."
    if (err.error.erroresBackend) {
      msg = ""
      for (let i = 0; i < err.error.erroresBackend.length; i++) {
        msg += "- " + err.error.erroresBackend[i] + "\n"
      }
    }
    this.alert(
      "Ha ocurrido un error",
      msg,
      "error",
    )
  }

  hide() {
    Swal.close()
  }

}
