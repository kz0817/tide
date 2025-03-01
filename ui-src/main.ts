document.addEventListener('DOMContentLoaded', () => {
    showFileList('/');
});

interface DirEntry {
  name: string;
  isDir: boolean;
  size: number;
  modifiedTime: string;
}

interface FileList {
  location: string;
  entries: DirEntry[];
}

const createDirItemElement = (entry: DirEntry, currDir: string, outerElem: HTMLElement): void => {
  const iconElem: HTMLSpanElement = document.createElement('span');
  iconElem.textContent = '📁';
  outerElem.appendChild(iconElem);

  const elem: HTMLAnchorElement = document.createElement('a');
  elem.textContent = entry.name;
  elem.href = '#';
  elem.addEventListener('click', (event: MouseEvent) => {
      const parentDir: string = (currDir == '/') ? '' : currDir;
      showFileList(`${parentDir}/${entry.name}`);
  });
  outerElem.appendChild(elem);
}

const createFileItemElement = (entry: DirEntry, currDir: string, outerElem: HTMLElement): void => {
  const elem: HTMLAnchorElement = document.createElement('a');
  elem.textContent = entry.name;
  const parentDir: string = (currDir == '/') ? '' : currDir;
  elem.href = `/file${parentDir}/${entry.name}`;
  outerElem.appendChild(elem);
}

const createEntryElement = (entry: DirEntry, currDir: string): HTMLElement => {
  const outerElem: HTMLSpanElement = document.createElement('span');
  entry.isDir ? createDirItemElement(entry, currDir, outerElem)
              : createFileItemElement(entry, currDir, outerElem);
  return outerElem;
}

const removeAllChildren = (elem: HTMLElement): void => {
  while (elem.firstChild) {
    elem.removeChild(elem.firstChild);
  }
}

const setupLocation = (location: string): void => {
  const parent: HTMLElement = document.getElementById('location') as HTMLElement;
  removeAllChildren(parent);

  const dirArr: string[] = ['/'].concat(location.split('/').filter(s => s !== ''));
  let dir: string = '';
  dirArr.forEach((dirName: string) => {

    const buttonElem: HTMLButtonElement = document.createElement('button');
    buttonElem.textContent = dirName;

    dir = (dirName == '/') ? '/' : `${dir}/${dirName}`;
    buttonElem.setAttribute('data-location', dir);

    buttonElem.addEventListener('click', (event: MouseEvent) => {
      const targetElem = event.target as HTMLElement;
      const targetDir: string = targetElem.getAttribute('data-location')!;
      showFileList(targetDir);
    });

    parent.appendChild(buttonElem);
  });
}

const showFileList = async (dir: string): Promise<void> => {
  const url = `/api/filelist?location=${dir}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to call {url}`)
  }
  console.log(response);
  const fileList: FileList = await response.json();
  console.log(fileList);

  setupLocation(fileList.location);

  const entriesElem: HTMLUListElement = document.getElementById('entries') as HTMLUListElement;
  removeAllChildren(entriesElem);

  fileList.entries
  .map((entry: DirEntry) => {
    const liElem = document.createElement('li');
    liElem.appendChild(createEntryElement(entry, dir));
    return liElem;
  })
  .forEach((liElem: HTMLLIElement) => entriesElem.appendChild(liElem));
}
