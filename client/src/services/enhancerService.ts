import instance from './axios';

const test = async () => {
   const response = await instance.get('/enhancers', {
      responseType: 'blob',
   });

   return URL.createObjectURL(response.data);
};

const test2 = async () => {
   return (await instance.get('/enhancers')).data;
};

const enhancing = async (id, data) => {
   return (await instance.post(`/enhancers/${id}`, data)).data;
};

export { test, test2, enhancing };
