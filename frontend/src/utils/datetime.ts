const formatTime = (date: Date) => {
  const currentLocale = localStorage.getItem('arco-locale');
  if (currentLocale === 'zh-CN') {
    return `${date.getFullYear()}-${
      date.getMonth() + 1
    }-${date.getDate()} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
  }
  return `${
    date.getMonth() + 1
  }/${date.getDate()}/${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
};

const formatTimestamp = (timestamp: number | unknown) => {
  if (!timestamp) return '';
  if (typeof timestamp === 'string') {
    timestamp = Number(timestamp);
  }
  if (typeof timestamp !== 'number') return '';
  const date = new Date(timestamp * 1000);
  const currentLocale = localStorage.getItem('arco-locale') ?? 'en-US';
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'UTC',
  };
  return new Intl.DateTimeFormat(currentLocale, options).format(date);
};

export { formatTime, formatTimestamp };
