export const setup = (): void => {
  document.getElementById('uploadChooser')?.addEventListener('change', (event) => {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file: File = input.files[0];
      uploadFileWithProgress(file);
    }
  });
}

const uploadFileWithProgress = (file: File): void => {
    const xhr = new XMLHttpRequest();
    const progressBar = document.getElementById('uploadProgressBar') as HTMLProgressElement;

    xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.value = percentComplete;
        }
    });

    xhr.open('POST', '/api/upload', true);
    xhr.setRequestHeader('Content-Type', 'application/octet-stream');
    xhr.setRequestHeader('X-File-Name', file.name);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                console.log('File uploaded successfully:', xhr.responseText);
            } else {
                console.error('Error uploading file:', xhr.statusText);
            }
        }
    };

    xhr.send(file);
}
