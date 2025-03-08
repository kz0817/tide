import { Context } from './context.js';

export const setup = (ctx: Context): void => {
  document.getElementById('uploadChooser')?.addEventListener('change', (event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file: File = input.files[0];
      uploadFileWithProgress(file, ctx);
    }
  });
}

const uploadFileWithProgress = (file: File, ctx: Context): void => {
    const xhr = new XMLHttpRequest();
    const progressBar = document.getElementById('uploadProgressBar') as HTMLProgressElement;
    const message = document.getElementById('uploadMessage') as HTMLSpanElement;
    progressBar.value = 0;
    message.textContent = 'uploading';

    xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.value = percentComplete;
        }
    });

    xhr.open('POST', '/api/upload', true);
    xhr.setRequestHeader('Content-Type', 'application/octet-stream');
    xhr.setRequestHeader('X-File-Name', file.name);
    xhr.setRequestHeader('X-File-Dir', ctx.presentDir);

    xhr.onreadystatechange = (): void => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status >= 200 && xhr.status < 300) {
                message.textContent = 'Completed';
                ctx.updateList();
            } else if (xhr.status == 409) {
                message.textContent = 'Erorr: File already exists';
            } else {
                console.log(xhr);
                message.textContent = `Error: ${xhr.statusText}`;
            }
        }
    };

    xhr.send(file);
}
